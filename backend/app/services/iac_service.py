"""
IaC 코드 생성 서비스
"""
from typing import Dict, Any, Optional
from uuid import UUID
import json
import re

from app.repositories.interfaces.infrastructure_repository import IInfrastructureRepository
from app.repositories.interfaces.iac_repository import IIaCRepository
from app.domain.entities.iac_code import IaCCode
from app.services.llm_service import LLMService


class IaCService:
    """
    IaC 코드 생성 서비스
    """
    
    def __init__(
        self,
        infrastructure_repository: IInfrastructureRepository,
        iac_repository: IIaCRepository,
        llm_service: Optional[LLMService] = None
    ):
        self.infrastructure_repository = infrastructure_repository
        self.iac_repository = iac_repository
        self.llm_service = llm_service or LLMService()
    
    async def generate_terraform_code(
        self,
        infrastructure_id: UUID,
        iac_tool: str = "terraform"
    ) -> IaCCode:
        """
        Terraform 코드 생성
        """
        infrastructure = self.infrastructure_repository.get_by_id(infrastructure_id)
        if not infrastructure:
            raise ValueError(f"Infrastructure {infrastructure_id} not found")
        
        # 기존 코드의 최신 버전 확인
        existing_codes = self.iac_repository.get_by_infrastructure_id(infrastructure_id)
        next_version = max([code.version for code in existing_codes], default=0) + 1
        
        # 이전 버전을 is_current=False로 설정
        for code in existing_codes:
            if code.is_current:
                code.is_current = False
                self.iac_repository.update(code)
        
        # LLM을 통한 Terraform 코드 생성
        terraform_code = await self._generate_with_llm(infrastructure, iac_tool)
        
        # 코드 검증
        validation_status, validation_errors = await self._validate_code(terraform_code, iac_tool)
        
        # IaC 코드 엔티티 생성
        iac_code = IaCCode(
            infrastructure_design_id=infrastructure_id,
            iac_tool=iac_tool,
            version=next_version,
            code_content=terraform_code,
            validation_status=validation_status,
            validation_errors=validation_errors,
            is_current=True,
            created_by="system"
        )
        
        # 저장
        created = self.iac_repository.create(iac_code)
        return created
    
    async def _generate_with_llm(
        self,
        infrastructure,
        iac_tool: str
    ) -> str:
        """LLM을 통한 IaC 코드 생성"""
        from langchain.schema import HumanMessage, SystemMessage
        
        llm = self.llm_service._get_llm()
        
        system_prompt = f"""당신은 {iac_tool} 전문가입니다. 인프라 아키텍처를 기반으로 {iac_tool} 코드를 생성하세요.

코드만 응답하고, 설명이나 마크다운 코드 블록은 포함하지 마세요."""
        
        architecture_json = json.dumps(infrastructure.architecture, ensure_ascii=False, indent=2)
        
        user_prompt = f"""인프라 아키텍처:
{architecture_json}

프로바이더: {infrastructure.provider or 'aws'}
설계 유형: {infrastructure.design_type}

위 아키텍처를 기반으로 {iac_tool} 코드를 생성하세요. 코드만 응답하세요."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # LLM 호출
        response = llm(messages)
        code = response.content
        
        # 마크다운 코드 블록 제거
        if "```" in code:
            # terraform, hcl 등의 언어 태그 제거
            code = re.sub(r'```\w*\n?', '', code)
            code = re.sub(r'```\n?', '', code)
            code = code.strip()
        
        return code
    
    async def _validate_code(self, code: str, iac_tool: str) -> tuple[str, Optional[Dict[str, Any]]]:
        """코드 검증"""
        if iac_tool == "terraform":
            # Terraform 코드 기본 검증 (구문 검사)
            # 실제로는 terraform validate를 실행해야 하지만, 여기서는 기본 검증만
            errors = []
            
            # 기본적인 구문 검사
            if not code.strip():
                errors.append("코드가 비어있습니다")
            
            # 필수 키워드 확인
            required_keywords = ["resource", "provider"]
            for keyword in required_keywords:
                if keyword not in code.lower():
                    errors.append(f"필수 키워드 '{keyword}'가 없습니다")
            
            if errors:
                return "invalid", {"errors": errors}
            
            return "valid", None
        
        # 다른 도구는 기본적으로 valid로 처리
        return "pending", None
    
    async def modify_code_with_prompt(
        self,
        iac_code_id: UUID,
        modification_prompt: str
    ) -> IaCCode:
        """프롬프트 기반 코드 수정"""
        iac_code = self.iac_repository.get_by_id(iac_code_id)
        if not iac_code:
            raise ValueError(f"IaC code {iac_code_id} not found")
        
        infrastructure = self.infrastructure_repository.get_by_id(iac_code.infrastructure_design_id)
        if not infrastructure:
            raise ValueError(f"Infrastructure not found")
        
        # 기존 코드와 수정 요청을 함께 LLM에 전달
        from langchain.schema import HumanMessage, SystemMessage
        
        llm = self.llm_service._get_llm()
        
        system_prompt = f"""당신은 {iac_code.iac_tool} 전문가입니다. 기존 코드를 수정 요청에 따라 수정하세요.

코드만 응답하고, 설명이나 마크다운 코드 블록은 포함하지 마세요."""
        
        user_prompt = f"""기존 코드:
{iac_code.code_content}

수정 요청:
{modification_prompt}

위 수정 요청에 따라 코드를 수정하세요. 코드만 응답하세요."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # LLM 호출
        response = llm(messages)
        modified_code = response.content
        
        # 마크다운 코드 블록 제거
        if "```" in modified_code:
            modified_code = re.sub(r'```\w*\n?', '', modified_code)
            modified_code = re.sub(r'```\n?', '', modified_code)
            modified_code = modified_code.strip()
        
        # 코드 검증
        validation_status, validation_errors = await self._validate_code(modified_code, iac_code.iac_tool)
        
        # 새 버전 생성
        existing_codes = self.iac_repository.get_by_infrastructure_id(iac_code.infrastructure_design_id)
        next_version = max([code.version for code in existing_codes], default=0) + 1
        
        # 이전 버전을 is_current=False로 설정
        for code in existing_codes:
            if code.is_current:
                code.is_current = False
                self.iac_repository.update(code)
        
        # 새 IaC 코드 엔티티 생성
        new_iac_code = IaCCode(
            infrastructure_design_id=iac_code.infrastructure_design_id,
            iac_tool=iac_code.iac_tool,
            version=next_version,
            code_content=modified_code,
            validation_status=validation_status,
            validation_errors=validation_errors,
            is_current=True,
            created_by="user_prompt"
        )
        
        # 저장
        created = self.iac_repository.create(new_iac_code)
        return created
    
    def get_code_diff(self, code1: str, code2: str) -> Dict[str, Any]:
        """코드 diff 생성"""
        # 간단한 diff (실제로는 difflib 사용 권장)
        lines1 = code1.split('\n')
        lines2 = code2.split('\n')
        
        added = [line for line in lines2 if line not in lines1]
        removed = [line for line in lines1 if line not in lines2]
        
        return {
            "added_lines": added,
            "removed_lines": removed,
            "added_count": len(added),
            "removed_count": len(removed)
        }

