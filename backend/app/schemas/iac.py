"""
IaC 코드 스키마 (Pydantic)
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.domain.entities.iac_code import IaCCode


class IaCCodeResponse(BaseModel):
    """IaC 코드 응답 스키마"""
    id: UUID
    infrastructure_design_id: UUID
    iac_tool: str
    version: int
    code_content: str
    validation_status: str
    validation_errors: Optional[Dict[str, Any]] = None
    is_current: bool
    created_at: datetime
    created_by: Optional[str] = None
    
    @classmethod
    def from_entity(cls, entity: IaCCode) -> "IaCCodeResponse":
        """도메인 엔티티로부터 스키마 생성"""
        return cls(**entity.dict())
    
    class Config:
        from_attributes = True


class IaCCodeModifyRequest(BaseModel):
    """IaC 코드 수정 요청 스키마"""
    prompt: str = Field(..., min_length=1, description="코드 수정을 위한 프롬프트")

