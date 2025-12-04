"""
인프라 설계 서비스
"""
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.core.config import settings
from app.repositories.interfaces.requirement_repository import IRequirementRepository
from app.repositories.interfaces.infrastructure_repository import IInfrastructureRepository
from app.domain.entities.infrastructure import Infrastructure
from app.services.llm_service import LLMService


class InfrastructureService:
    """
    인프라 설계 서비스
    """
    
    def __init__(
        self,
        requirement_repository: IRequirementRepository,
        infrastructure_repository: IInfrastructureRepository,
        llm_service: Optional[LLMService] = None
    ):
        self.requirement_repository = requirement_repository
        self.infrastructure_repository = infrastructure_repository
        self.llm_service = llm_service or LLMService()
    
    async def design_infrastructure(
        self,
        requirement_id: UUID,
        design_type: str = "cloud"  # 'onprem', 'cloud', 'hybrid'
    ) -> Infrastructure:
        """
        인프라 설계 생성
        """
        requirement = self.requirement_repository.get_by_id(requirement_id)
        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")
        
        # 요구사항 분석 데이터 가져오기
        analysis_data = requirement.structured_data or {}
        
        # LLM을 통한 인프라 설계
        architecture = await self._design_with_llm(analysis_data, design_type)
        
        # 비용 산정
        cost_estimate = self._estimate_cost(architecture, design_type)
        
        # 인프라 설계 엔티티 생성
        infrastructure = Infrastructure(
            requirement_id=requirement_id,
            design_type=design_type,
            provider=self._determine_provider(design_type, analysis_data),
            architecture=architecture,
            cost_estimate=cost_estimate,
            status="draft",
        )
        
        # 저장
        created = self.infrastructure_repository.create(infrastructure)
        return created
    
    async def _design_with_llm(
        self,
        analysis_data: Dict[str, Any],
        design_type: str
    ) -> Dict[str, Any]:
        """LLM을 통한 인프라 설계"""
        from langchain.prompts import ChatPromptTemplate
        from langchain.schema import HumanMessage, SystemMessage
        
        llm = self.llm_service._get_llm()
        
        system_prompt = """당신은 인프라 아키텍처 전문가입니다. 요구사항을 분석하여 최적의 인프라 아키텍처를 설계하세요.

다음 JSON 형식으로 응답하세요:
{
    "components": [
        {
            "name": "컴포넌트 이름",
            "type": "컴포넌트 타입 (예: web_server, database, cache 등)",
            "spec": "스펙 (예: t3.medium, db.t3.small 등)",
            "count": 2,
            "description": "설명"
        }
    ],
    "networking": {
        "vpc": "VPC 설정",
        "subnets": ["서브넷 정보"],
        "security_groups": ["보안 그룹 정보"]
    },
    "storage": {
        "type": "스토리지 타입",
        "size": "크기"
    },
    "monitoring": {
        "enabled": true,
        "tools": ["모니터링 도구"]
    }
}"""
        
        design_type_kr = {
            "onprem": "온프레미스",
            "cloud": "클라우드",
            "hybrid": "하이브리드"
        }.get(design_type, design_type)
        
        user_prompt = f"""요구사항 분석 결과:
{self._format_analysis_data(analysis_data)}

배포 유형: {design_type_kr}

위 요구사항에 맞는 {design_type_kr} 인프라 아키텍처를 설계하세요. JSON 형식으로 응답하세요."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # LLM 호출
        response = llm(messages)
        
        # JSON 파싱
        import json
        try:
            response_text = response.content
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            architecture = json.loads(response_text)
        except json.JSONDecodeError:
            # 기본 구조 반환
            architecture = {
                "components": [],
                "networking": {},
                "storage": {},
                "monitoring": {},
                "raw_response": response.content
            }
        
        return architecture
    
    def _format_analysis_data(self, analysis_data: Dict[str, Any]) -> str:
        """분석 데이터를 텍스트로 포맷팅"""
        parts = []
        for key, value in analysis_data.items():
            if isinstance(value, list):
                parts.append(f"{key}: {', '.join(map(str, value))}")
            else:
                parts.append(f"{key}: {value}")
        return "\n".join(parts)
    
    def _determine_provider(
        self,
        design_type: str,
        analysis_data: Dict[str, Any]
    ) -> str:
        """프로바이더 결정"""
        if design_type == "onprem":
            return "onprem"
        
        # 클라우드 프로바이더는 기본적으로 AWS로 설정 (추후 확장 가능)
        preferred_provider = analysis_data.get("preferred_provider", "aws")
        if preferred_provider in ["aws", "azure", "gcp"]:
            return preferred_provider
        return "aws"
    
    def _estimate_cost(self, architecture: Dict[str, Any], design_type: str) -> Dict[str, Any]:
        """비용 산정 (기본 계산식)"""
        # 실제로는 클라우드 API를 호출하거나 상세한 계산식이 필요
        # 여기서는 기본적인 추정치만 제공
        
        components = architecture.get("components", [])
        total_monthly_cost = 0
        cost_breakdown = []
        
        # 기본 비용 추정 (예시)
        cost_per_component = {
            "web_server": 50000,  # 월 5만원
            "database": 100000,   # 월 10만원
            "cache": 30000,       # 월 3만원
            "storage": 20000,     # 월 2만원
        }
        
        for component in components:
            comp_type = component.get("type", "")
            count = component.get("count", 1)
            base_cost = cost_per_component.get(comp_type, 50000)
            component_cost = base_cost * count
            
            total_monthly_cost += component_cost
            cost_breakdown.append({
                "component": component.get("name", comp_type),
                "type": comp_type,
                "count": count,
                "monthly_cost": component_cost
            })
        
        return {
            "total_monthly": total_monthly_cost,
            "total_yearly": total_monthly_cost * 12,
            "currency": "KRW",
            "breakdown": cost_breakdown,
            "note": "이 비용은 추정치이며 실제 비용과 다를 수 있습니다."
        }
    
    async def compare_designs(
        self,
        requirement_id: UUID
    ) -> Dict[str, Any]:
        """온프레미스와 클라우드 설계안 비교"""
        infrastructures = self.infrastructure_repository.get_by_requirement_id(requirement_id)
        
        onprem_design = next((infra for infra in infrastructures if infra.design_type == "onprem"), None)
        cloud_design = next((infra for infra in infrastructures if infra.design_type == "cloud"), None)
        
        comparison = {
            "onprem": {
                "exists": onprem_design is not None,
                "cost": onprem_design.cost_estimate if onprem_design else None,
                "id": str(onprem_design.id) if onprem_design else None
            },
            "cloud": {
                "exists": cloud_design is not None,
                "cost": cloud_design.cost_estimate if cloud_design else None,
                "id": str(cloud_design.id) if cloud_design else None
            }
        }
        
        # 비용 비교
        if onprem_design and cloud_design:
            onprem_cost = onprem_design.cost_estimate.get("total_monthly", 0) if onprem_design.cost_estimate else 0
            cloud_cost = cloud_design.cost_estimate.get("total_monthly", 0) if cloud_design.cost_estimate else 0
            
            comparison["cost_difference"] = {
                "monthly": cloud_cost - onprem_cost,
                "yearly": (cloud_cost - onprem_cost) * 12,
                "cheaper": "onprem" if onprem_cost < cloud_cost else "cloud"
            }
        
        return comparison

