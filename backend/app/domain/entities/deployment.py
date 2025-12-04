"""
배포 도메인 엔티티
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Deployment:
    """
    배포 도메인 엔티티
    """
    id: Optional[UUID] = None
    infrastructure_design_id: UUID = None
    iac_code_id: UUID = None
    status: str = "pending"  # 'pending', 'deploying', 'success', 'failed', 'rolled_back'
    deployment_log: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "infrastructure_design_id": self.infrastructure_design_id,
            "iac_code_id": self.iac_code_id,
            "status": self.status,
            "deployment_log": self.deployment_log,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "created_at": self.created_at,
        }

