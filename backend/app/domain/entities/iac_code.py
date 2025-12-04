"""
IaC 코드 도메인 엔티티
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


@dataclass
class IaCCode:
    """
    IaC 코드 도메인 엔티티
    """
    id: Optional[UUID] = None
    infrastructure_design_id: UUID = None
    iac_tool: str = None  # 'terraform', 'ansible', 'kubernetes'
    version: int = 1
    code_content: str = None
    validation_status: str = "pending"  # 'pending', 'valid', 'invalid'
    validation_errors: Optional[Dict[str, Any]] = None
    is_current: bool = True
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None  # 'system', 'user_prompt'
    
    def dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "infrastructure_design_id": self.infrastructure_design_id,
            "iac_tool": self.iac_tool,
            "version": self.version,
            "code_content": self.code_content,
            "validation_status": self.validation_status,
            "validation_errors": self.validation_errors,
            "is_current": self.is_current,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

