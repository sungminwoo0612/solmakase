"""
채팅 메시지 도메인 엔티티
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class ChatMessage:
    """
    채팅 메시지 도메인 엔티티
    """
    id: Optional[UUID] = None
    requirement_id: UUID = None
    role: str = None  # 'user', 'assistant'
    message: str = None
    created_at: Optional[datetime] = None
    
    def dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "requirement_id": self.requirement_id,
            "role": self.role,
            "message": self.message,
            "created_at": self.created_at,
        }
