"""
채팅 메시지 리포지토리 구현체
"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.interfaces.chat_repository import IChatRepository
from app.domain.entities.chat_message import ChatMessage
from app.models.chat_message import ChatMessageModel


class ChatRepository(IChatRepository):
    """
    채팅 메시지 리포지토리 구현체
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, chat_message: ChatMessage) -> ChatMessage:
        """채팅 메시지 생성"""
        db_chat = ChatMessageModel(**chat_message.dict())
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return self._to_entity(db_chat)
    
    def get_by_requirement_id(self, requirement_id: UUID) -> List[ChatMessage]:
        """요구사항 ID로 채팅 메시지 목록 조회"""
        db_chats = self.db.query(ChatMessageModel).filter(
            ChatMessageModel.requirement_id == requirement_id
        ).order_by(ChatMessageModel.created_at.asc()).all()
        return [self._to_entity(chat) for chat in db_chats]
    
    def _to_entity(self, db_model: ChatMessageModel) -> ChatMessage:
        """ORM 모델을 도메인 엔티티로 변환"""
        return ChatMessage(**db_model.__dict__)

