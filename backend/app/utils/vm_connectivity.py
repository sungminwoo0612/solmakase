"""
VM 연결성 확인 유틸리티

VirtualBox, Vagrant 등의 VM과의 통신 여부를 확인하는 유틸리티
"""
import asyncio
import subprocess
import socket
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from app.core.logging_config import get_logger
from app.core.config import settings

logger = get_logger("app.utils.vm_connectivity")


class VMConnectivityChecker:
    """
    VM 연결성 확인기
    
    - VirtualBox VM 상태 확인
    - SSH 연결 확인
    - 네트워크 연결 확인
    - Vagrant 상태 확인
    """
    
    def __init__(self, vm_name: Optional[str] = None):
        self.vm_name = vm_name or "Solmakase-Dev-Server"
    
    async def check_virtualbox_vm_status(self) -> Dict[str, Any]:
        """
        VirtualBox VM 상태 확인
        
        Returns:
            VM 상태 정보
        """
        try:
            # VBoxManage 명령어로 VM 상태 확인
            result = await self._run_command(
                ["VBoxManage", "showvminfo", self.vm_name, "--machinereadable"]
            )
            
            if not result[0]:
                return {
                    "available": False,
                    "error": f"VM을 찾을 수 없습니다: {self.vm_name}",
                    "status": "not_found"
                }
            
            # VM 정보 파싱
            vm_info = {}
            for line in result[1].split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    vm_info[key] = value.strip('"')
            
            # VM 상태 확인
            vm_state = vm_info.get("VMState", "unknown")
            is_running = vm_state == "running"
            
            return {
                "available": True,
                "vm_name": self.vm_name,
                "status": vm_state,
                "is_running": is_running,
                "uuid": vm_info.get("UUID", ""),
                "memory": vm_info.get("memory", ""),
                "cpus": vm_info.get("cpus", ""),
            }
            
        except FileNotFoundError:
            return {
                "available": False,
                "error": "VBoxManage를 찾을 수 없습니다. VirtualBox가 설치되어 있는지 확인하세요.",
                "status": "vbox_not_installed"
            }
        except Exception as e:
            logger.exception(f"VirtualBox VM 상태 확인 실패: {str(e)}")
            return {
                "available": False,
                "error": str(e),
                "status": "error"
            }
    
    async def check_vagrant_status(self, vagrant_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Vagrant 상태 확인
        
        Args:
            vagrant_dir: Vagrantfile이 있는 디렉토리 (기본값: 현재 디렉토리)
            
        Returns:
            Vagrant 상태 정보
        """
        try:
            if vagrant_dir:
                work_dir = Path(vagrant_dir)
            else:
                # 프로젝트 루트 찾기
                work_dir = Path(__file__).resolve().parents[3]
            
            # vagrant status 명령어 실행
            result = await self._run_command(
                ["vagrant", "status"],
                cwd=str(work_dir)
            )
            
            if not result[0]:
                return {
                    "available": False,
                    "error": "Vagrant 상태 확인 실패",
                    "status": "error",
                    "output": result[1]
                }
            
            # 상태 파싱
            output = result[1]
            is_running = "running" in output.lower()
            
            return {
                "available": True,
                "is_running": is_running,
                "status": "running" if is_running else "stopped",
                "output": output
            }
            
        except FileNotFoundError:
            return {
                "available": False,
                "error": "vagrant 명령어를 찾을 수 없습니다. Vagrant가 설치되어 있는지 확인하세요.",
                "status": "vagrant_not_installed"
            }
        except Exception as e:
            logger.exception(f"Vagrant 상태 확인 실패: {str(e)}")
            return {
                "available": False,
                "error": str(e),
                "status": "error"
            }
    
    async def check_ssh_connection(
        self,
        host: str = "localhost",
        port: int = 22,
        timeout: int = 5
    ) -> Dict[str, Any]:
        """
        SSH 연결 확인
        
        Args:
            host: 호스트 주소
            port: SSH 포트
            timeout: 타임아웃 (초)
            
        Returns:
            SSH 연결 상태
        """
        try:
            # 소켓 연결 시도
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            is_connected = result == 0
            
            return {
                "available": is_connected,
                "host": host,
                "port": port,
                "status": "connected" if is_connected else "disconnected",
                "error": None if is_connected else f"포트 {port}에 연결할 수 없습니다"
            }
            
        except Exception as e:
            logger.exception(f"SSH 연결 확인 실패: {str(e)}")
            return {
                "available": False,
                "host": host,
                "port": port,
                "status": "error",
                "error": str(e)
            }
    
    async def check_vagrant_ssh(self, vagrant_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Vagrant SSH 연결 확인
        
        Args:
            vagrant_dir: Vagrantfile이 있는 디렉토리
            
        Returns:
            SSH 연결 상태
        """
        try:
            if vagrant_dir:
                work_dir = Path(vagrant_dir)
            else:
                work_dir = Path(__file__).resolve().parents[3]
            
            # vagrant ssh-config 명령어로 SSH 설정 확인
            result = await self._run_command(
                ["vagrant", "ssh-config"],
                cwd=str(work_dir)
            )
            
            if not result[0]:
                return {
                    "available": False,
                    "error": "Vagrant SSH 설정을 가져올 수 없습니다",
                    "status": "error"
                }
            
            # SSH 설정 파싱
            ssh_config = {}
            for line in result[1].split('\n'):
                if ' ' in line:
                    parts = line.strip().split(' ', 1)
                    if len(parts) == 2:
                        key, value = parts
                        ssh_config[key] = value
            
            # SSH 연결 테스트
            host = ssh_config.get("HostName", "localhost")
            port = int(ssh_config.get("Port", 22))
            
            ssh_status = await self.check_ssh_connection(host, port)
            
            return {
                "available": ssh_status["available"],
                "host": host,
                "port": port,
                "user": ssh_config.get("User", "vagrant"),
                "status": ssh_status["status"],
                "ssh_config": ssh_config,
                "error": ssh_status.get("error")
            }
            
        except Exception as e:
            logger.exception(f"Vagrant SSH 확인 실패: {str(e)}")
            return {
                "available": False,
                "error": str(e),
                "status": "error"
            }
    
    async def check_network_connectivity(
        self,
        hosts: List[Tuple[str, int]] = None,
        service_names: Optional[Dict[Tuple[str, int], str]] = None
    ) -> Dict[str, Any]:
        """
        네트워크 연결 확인
        
        Args:
            hosts: 확인할 호스트와 포트 리스트 [(host, port), ...]
            service_names: 포트별 서비스 이름 매핑 {(host, port): "서비스명"}
            
        Returns:
            네트워크 연결 상태
        """
        if hosts is None:
            # 기본 포트 확인
            hosts = [
                ("localhost", 8000),  # FastAPI
                ("localhost", 5173),  # Vite
                ("localhost", 5432),  # PostgreSQL
                ("localhost", 6379),  # Redis
            ]
        
        if service_names is None:
            service_names = {
                ("localhost", 8000): "FastAPI (Backend)",
                ("localhost", 5173): "Vite (Frontend)",
                ("localhost", 5432): "PostgreSQL (Database)",
                ("localhost", 6379): "Redis (Cache)",
            }
        
        results = {}
        connected_count = 0
        total_count = len(hosts)
        
        for host, port in hosts:
            service_name = service_names.get((host, port), f"{host}:{port}")
            key = f"{host}:{port}"
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()
                
                is_connected = result == 0
                if is_connected:
                    connected_count += 1
                
                results[key] = {
                    "available": is_connected,
                    "status": "connected" if is_connected else "disconnected",
                    "service": service_name,
                    "host": host,
                    "port": port,
                    "error": None if is_connected else self._get_connection_error_message(service_name, port)
                }
            except Exception as e:
                results[key] = {
                    "available": False,
                    "status": "error",
                    "service": service_name,
                    "host": host,
                    "port": port,
                    "error": str(e)
                }
        
        # 상태 판단
        if connected_count == total_count:
            status = "all_connected"
            available = True
        elif connected_count > 0:
            status = "partial"
            available = False
        else:
            status = "all_disconnected"
            available = False
        
        # 필수 서비스 확인 (FastAPI는 필수, 나머지는 선택적)
        required_services = [("localhost", 8000)]
        required_connected = all(
            results.get(f"{host}:{port}", {}).get("available", False)
            for host, port in required_services
        )
        
        return {
            "available": available,
            "status": status,
            "connected_count": connected_count,
            "total_count": total_count,
            "required_services_ok": required_connected,
            "connections": results,
            "summary": {
                "connected": [k for k, v in results.items() if v["available"]],
                "disconnected": [k for k, v in results.items() if not v["available"]]
            }
        }
    
    def _get_connection_error_message(self, service_name: str, port: int) -> str:
        """연결 실패 시 안내 메시지 생성"""
        messages = {
            "PostgreSQL (Database)": f"PostgreSQL이 실행되지 않았거나 포트 {port}에서 접근할 수 없습니다. "
                                   f"서비스를 시작하려면: sudo systemctl start postgresql 또는 "
                                   f"docker-compose up -d postgres",
            "Redis (Cache)": f"Redis가 실행되지 않았거나 포트 {port}에서 접근할 수 없습니다. "
                           f"서비스를 시작하려면: sudo systemctl start redis 또는 "
                           f"docker-compose up -d redis",
            "FastAPI (Backend)": f"FastAPI 백엔드가 실행되지 않았거나 포트 {port}에서 접근할 수 없습니다. "
                               f"서비스를 시작하려면: cd backend && uvicorn main:app --host 0.0.0.0 --port {port}",
            "Vite (Frontend)": f"Vite 프론트엔드가 실행되지 않았거나 포트 {port}에서 접근할 수 없습니다. "
                             f"서비스를 시작하려면: cd front && npm run dev -- --host 0.0.0.0 --port {port}",
        }
        return messages.get(service_name, f"포트 {port}에 연결할 수 없습니다.")
    
    async def check_all(self, vagrant_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        모든 연결성 확인
        
        Args:
            vagrant_dir: Vagrantfile이 있는 디렉토리
            
        Returns:
            전체 연결성 상태
        """
        results = {
            "virtualbox": await self.check_virtualbox_vm_status(),
            "vagrant": await self.check_vagrant_status(vagrant_dir),
            "vagrant_ssh": await self.check_vagrant_ssh(vagrant_dir),
            "network": await self.check_network_connectivity(),
        }
        
        # 전체 상태 판단
        all_ok = (
            results["virtualbox"].get("is_running", False) or
            results["vagrant"].get("is_running", False)
        ) and results["vagrant_ssh"].get("available", False)
        
        results["overall"] = {
            "available": all_ok,
            "status": "ready" if all_ok else "not_ready"
        }
        
        logger.info(f"VM 연결성 확인 완료: overall_status={results['overall']['status']}")
        
        return results
    
    async def _run_command(
        self,
        cmd: list,
        cwd: Optional[str] = None,
        timeout: int = 10
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

