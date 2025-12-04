"""
인프라 설계 도메인 엔티티
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


@dataclass
class Infrastructure:
    """
    인프라 설계 도메인 엔티티
    """
    id: Optional[UUID] = None
    requirement_id: UUID = None
    design_type: str = None  # 'onprem', 'cloud', 'hybrid'
    provider: Optional[str] = None  # 'aws', 'azure', 'gcp', 'onprem'
    architecture: Dict[str, Any] = None
    cost_estimate: Optional[Dict[str, Any]] = None
    plan_document: Optional[str] = None
    status: str = "draft"  # 'draft', 'approved', 'deployed'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "requirement_id": self.requirement_id,
            "design_type": self.design_type,
            "provider": self.provider,
            "architecture": self.architecture,
            "cost_estimate": self.cost_estimate,
            "plan_document": self.plan_document,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

