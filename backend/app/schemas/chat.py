"""
채팅 메시지 스키마 (Pydantic)
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.domain.entities.chat_message import ChatMessage


class ChatMessageCreate(BaseModel):
    """채팅 메시지 생성 스키마"""
    requirement_id: UUID
    role: str = Field(..., description="메시지 역할: user, assistant")
    message: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    """채팅 메시지 응답 스키마"""
    id: UUID
    requirement_id: UUID
    role: str
    message: str
    created_at: datetime
    
    @classmethod
    def from_entity(cls, entity: ChatMessage) -> "ChatMessageResponse":
        """도메인 엔티티로부터 스키마 생성"""
        return cls(**entity.dict())
    
    class Config:
        from_attributes = True

