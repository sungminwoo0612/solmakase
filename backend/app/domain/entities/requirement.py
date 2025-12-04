"""
요구사항 도메인 엔티티
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


@dataclass
class Requirement:
    """
    요구사항 도메인 엔티티
    """
    id: Optional[UUID] = None
    user_id: UUID = None
    input_type: str = None  # 'survey', 'document', 'chat', 'expert'
    service_type: Optional[str] = None
    deployment_type: Optional[str] = None  # 'onprem', 'cloud', 'hybrid'
    scale: Optional[str] = None  # 'small', 'medium', 'large'
    budget: Optional[float] = None
    has_ops_team: Optional[bool] = None
    special_requirements: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    status: str = "pending"  # 'pending', 'analyzing', 'completed', 'failed'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "input_type": self.input_type,
            "service_type": self.service_type,
            "deployment_type": self.deployment_type,
            "scale": self.scale,
            "budget": self.budget,
            "has_ops_team": self.has_ops_team,
            "special_requirements": self.special_requirements,
            "structured_data": self.structured_data,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

