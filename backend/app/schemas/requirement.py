"""
요구사항 스키마 (Pydantic)
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.domain.entities.requirement import Requirement


class RequirementCreate(BaseModel):
    """요구사항 생성 스키마"""
    user_id: UUID
    input_type: str = Field(..., description="입력 유형: survey, document, chat, expert")
    service_type: Optional[str] = None
    deployment_type: Optional[str] = Field(None, description="onprem, cloud, hybrid")
    scale: Optional[str] = Field(None, description="small, medium, large")
    budget: Optional[float] = None
    has_ops_team: Optional[bool] = None
    special_requirements: Optional[str] = None


class RequirementResponse(BaseModel):
    """요구사항 응답 스키마"""
    id: UUID
    user_id: UUID
    input_type: str
    service_type: Optional[str] = None
    deployment_type: Optional[str] = None
    scale: Optional[str] = None
    budget: Optional[float] = None
    has_ops_team: Optional[bool] = None
    special_requirements: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_entity(cls, entity: Requirement) -> "RequirementResponse":
        """도메인 엔티티로부터 스키마 생성"""
        return cls(**entity.dict())
    
    class Config:
        from_attributes = True

