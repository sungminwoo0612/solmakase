"""
배포 실행기 유틸리티

Terraform, Ansible 등의 IaC 도구를 실행하는 유틸리티
"""
import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from uuid import UUID

from app.core.logging_config import get_logger
from app.core.config import settings
from app.utils.vm_connectivity import VMConnectivityChecker

logger = get_logger("app.utils.deployment_executor")


class DeploymentExecutor:
    """
    배포 실행기
    
    - Terraform 실행
    - Ansible 실행
    - 배포 로그 수집
    """
    
    def __init__(self, deployment_id: UUID, vm_name: Optional[str] = None):
        self.deployment_id = deployment_id
        self.work_dir = None
        self.vm_checker = VMConnectivityChecker(vm_name=vm_name)
    
    async def execute_terraform(
        self,
        terraform_code: str,
        variables: Optional[Dict[str, Any]] = None,
        check_vm_connectivity: bool = True
    ) -> Tuple[bool, str]:
        """
        Terraform 실행
        
        Args:
            terraform_code: Terraform 코드 내용
            variables: Terraform 변수 (선택)
            check_vm_connectivity: 배포 전 VM 연결성 확인 여부
            
        Returns:
            (성공 여부, 로그)
        """
        try:
            # VM 연결성 확인 (선택적)
            if check_vm_connectivity:
                logger.info(f"배포 전 VM 연결성 확인: deployment_id={self.deployment_id}")
                connectivity = await self.vm_checker.check_all()
                
                if not connectivity["overall"]["available"]:
                    warning_msg = f"VM 연결성 확인 실패. 배포를 계속 진행하지만 문제가 발생할 수 있습니다.\n{connectivity}"
                    logger.warning(warning_msg)
                    # 경고만 출력하고 계속 진행
            # 작업 디렉토리 생성
            self.work_dir = tempfile.mkdtemp(prefix=f"terraform-{self.deployment_id}-")
            logger.info(f"Terraform 작업 디렉토리 생성: {self.work_dir}")
            
            # Terraform 파일 작성
            main_tf_path = Path(self.work_dir) / "main.tf"
            main_tf_path.write_text(terraform_code, encoding="utf-8")
            
            # variables.tf 작성 (변수가 있는 경우)
            if variables:
                vars_content = self._generate_terraform_variables(variables)
                vars_tf_path = Path(self.work_dir) / "variables.tf"
                vars_tf_path.write_text(vars_content, encoding="utf-8")
                
                # terraform.tfvars 작성
                tfvars_content = self._generate_terraform_tfvars(variables)
                tfvars_path = Path(self.work_dir) / "terraform.tfvars"
                tfvars_path.write_text(tfvars_content, encoding="utf-8")
            
            # Terraform 초기화
            init_result = await self._run_command(
                ["terraform", "init"],
                cwd=self.work_dir
            )
            if not init_result[0]:
                return False, f"Terraform 초기화 실패:\n{init_result[1]}"
            
            # Terraform 검증
            validate_result = await self._run_command(
                ["terraform", "validate"],
                cwd=self.work_dir
            )
            if not validate_result[0]:
                return False, f"Terraform 검증 실패:\n{validate_result[1]}"
            
            # Terraform 플랜
            plan_result = await self._run_command(
                ["terraform", "plan", "-out=tfplan"],
                cwd=self.work_dir
            )
            if not plan_result[0]:
                return False, f"Terraform 플랜 실패:\n{plan_result[1]}"
            
            # Terraform 적용 (실제 배포)
            apply_result = await self._run_command(
                ["terraform", "apply", "-auto-approve", "tfplan"],
                cwd=self.work_dir
            )
            if not apply_result[0]:
                return False, f"Terraform 적용 실패:\n{apply_result[1]}"
            
            # 성공 로그 수집
            log = f"""Terraform 배포 성공

초기화:
{init_result[1]}

검증:
{validate_result[1]}

플랜:
{plan_result[1]}

적용:
{apply_result[1]}
"""
            
            logger.info(f"Terraform 배포 성공: deployment_id={self.deployment_id}")
            return True, log
            
        except Exception as e:
            error_msg = f"Terraform 실행 중 예외 발생: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
        finally:
            # 작업 디렉토리 정리 (선택적 - 디버깅을 위해 유지할 수도 있음)
            if self.work_dir and os.path.exists(self.work_dir):
                # 개발 환경에서는 디렉토리를 유지할 수 있음
                if settings.DEBUG:
                    logger.info(f"디버그 모드: 작업 디렉토리 유지 - {self.work_dir}")
                else:
                    shutil.rmtree(self.work_dir, ignore_errors=True)
                    logger.info(f"작업 디렉토리 삭제: {self.work_dir}")
    
    async def rollback_terraform(self) -> Tuple[bool, str]:
        """
        Terraform 롤백 (destroy)
        
        Returns:
            (성공 여부, 로그)
        """
        if not self.work_dir or not os.path.exists(self.work_dir):
            return False, "작업 디렉토리를 찾을 수 없습니다."
        
        try:
            # Terraform destroy
            destroy_result = await self._run_command(
                ["terraform", "destroy", "-auto-approve"],
                cwd=self.work_dir
            )
            
            if not destroy_result[0]:
                return False, f"Terraform 롤백 실패:\n{destroy_result[1]}"
            
            log = f"Terraform 롤백 성공:\n{destroy_result[1]}"
            logger.info(f"Terraform 롤백 성공: deployment_id={self.deployment_id}")
            return True, log
            
        except Exception as e:
            error_msg = f"Terraform 롤백 중 예외 발생: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
    
    async def execute_ansible(
        self,
        playbook_content: str,
        inventory_content: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Ansible 실행
        
        Args:
            playbook_content: Ansible playbook 내용
            inventory_content: Inventory 파일 내용 (선택)
            
        Returns:
            (성공 여부, 로그)
        """
        try:
            # 작업 디렉토리 생성
            self.work_dir = tempfile.mkdtemp(prefix=f"ansible-{self.deployment_id}-")
            logger.info(f"Ansible 작업 디렉토리 생성: {self.work_dir}")
            
            # Playbook 파일 작성
            playbook_path = Path(self.work_dir) / "playbook.yml"
            playbook_path.write_text(playbook_content, encoding="utf-8")
            
            # Inventory 파일 작성 (있는 경우)
            inventory_path = None
            if inventory_content:
                inventory_path = Path(self.work_dir) / "inventory.ini"
                inventory_path.write_text(inventory_content, encoding="utf-8")
            
            # Ansible 실행
            cmd = ["ansible-playbook", "playbook.yml"]
            if inventory_path:
                cmd.extend(["-i", str(inventory_path)])
            
            result = await self._run_command(cmd, cwd=self.work_dir)
            
            if not result[0]:
                return False, f"Ansible 실행 실패:\n{result[1]}"
            
            log = f"Ansible 배포 성공:\n{result[1]}"
            logger.info(f"Ansible 배포 성공: deployment_id={self.deployment_id}")
            return True, log
            
        except Exception as e:
            error_msg = f"Ansible 실행 중 예외 발생: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
        finally:
            if self.work_dir and os.path.exists(self.work_dir):
                if settings.DEBUG:
                    logger.info(f"디버그 모드: 작업 디렉토리 유지 - {self.work_dir}")
                else:
                    shutil.rmtree(self.work_dir, ignore_errors=True)
    
    async def _run_command(
        self,
        cmd: list,
        cwd: Optional[str] = None,
        timeout: int = 1800  # 30분
    ) -> Tuple[bool, str]:
        """
        명령어 실행
        
        Args:
            cmd: 실행할 명령어 리스트
            cwd: 작업 디렉토리
            timeout: 타임아웃 (초)
            
        Returns:
            (성공 여부, 출력)
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=cwd
            )
            
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            output = stdout.decode("utf-8", errors="replace")
            success = process.returncode == 0
            
            return success, output
            
        except asyncio.TimeoutError:
            error_msg = f"명령어 실행 타임아웃: {' '.join(cmd)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"명령어 실행 실패: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
    
    def _generate_terraform_variables(self, variables: Dict[str, Any]) -> str:
        """Terraform variables.tf 생성"""
        lines = []
        for key, value in variables.items():
            var_type = self._infer_terraform_type(value)
            lines.append(f'variable "{key}" {{')
            lines.append(f'  type = {var_type}')
            lines.append(f'  description = "Variable {key}"')
            lines.append('}')
            lines.append('')
        return '\n'.join(lines)
    
    def _generate_terraform_tfvars(self, variables: Dict[str, Any]) -> str:
        """Terraform terraform.tfvars 생성"""
        lines = []
        for key, value in variables.items():
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            elif isinstance(value, bool):
                lines.append(f'{key} = {str(value).lower()}')
            else:
                lines.append(f'{key} = {value}')
        return '\n'.join(lines)
    
    def _infer_terraform_type(self, value: Any) -> str:
        """값으로부터 Terraform 타입 추론"""
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "number"
        elif isinstance(value, (list, tuple)):
            return "list(any)"
        elif isinstance(value, dict):
            return "map(any)"
        else:
            return "string"

