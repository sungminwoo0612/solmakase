"""
인프라 설계 스키마 (Pydantic)
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.domain.entities.infrastructure import Infrastructure


class InfrastructureCreate(BaseModel):
    """인프라 설계 생성 스키마"""
    requirement_id: UUID
    design_type: str  # 'onprem', 'cloud', 'hybrid'
    provider: Optional[str] = None


class InfrastructureResponse(BaseModel):
    """인프라 설계 응답 스키마"""
    id: UUID
    requirement_id: UUID
    design_type: str
    provider: Optional[str] = None
    architecture: Dict[str, Any]
    cost_estimate: Optional[Dict[str, Any]] = None
    plan_document: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_entity(cls, entity: Infrastructure) -> "InfrastructureResponse":
        """도메인 엔티티로부터 스키마 생성"""
        return cls(**entity.dict())
    
    class Config:
        from_attributes = True

