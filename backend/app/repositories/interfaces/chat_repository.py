"""
채팅 메시지 리포지토리 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.chat_message import ChatMessage


class IChatRepository(ABC):
    """
    채팅 메시지 리포지토리 인터페이스
    """
    
    @abstractmethod
    def create(self, chat_message: ChatMessage) -> ChatMessage:
        """채팅 메시지 생성"""
        pass
    
    @abstractmethod
    def get_by_requirement_id(self, requirement_id: UUID) -> List[ChatMessage]:
        """요구사항 ID로 채팅 메시지 목록 조회"""
        pass

