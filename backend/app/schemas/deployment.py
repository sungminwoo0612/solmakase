"""
배포 스키마 (Pydantic)
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.domain.entities.deployment import Deployment


class DeploymentCreate(BaseModel):
    """배포 생성 스키마"""
    infrastructure_design_id: UUID
    iac_code_id: UUID


class DeploymentResponse(BaseModel):
    """배포 응답 스키마"""
    id: UUID
    infrastructure_design_id: UUID
    iac_code_id: UUID
    status: str  # 'pending', 'deploying', 'success', 'failed', 'rolled_back'
    deployment_log: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    @classmethod
    def from_entity(cls, entity: Deployment) -> "DeploymentResponse":
        """도메인 엔티티로부터 스키마 생성"""
        return cls(**entity.dict())
    
    class Config:
        from_attributes = True


class DeploymentUpdate(BaseModel):
    """배포 업데이트 스키마"""
    status: Optional[str] = None
    deployment_log: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

