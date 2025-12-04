"""
문서 리포지토리 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.entities.document import Document


class IDocumentRepository(ABC):
    """
    문서 리포지토리 인터페이스
    """
    
    @abstractmethod
    def create(self, document: Document) -> Document:
        """문서 생성"""
        pass
    
    @abstractmethod
    def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """ID로 문서 조회"""
        pass
    
    @abstractmethod
    def get_by_requirement_id(self, requirement_id: UUID) -> List[Document]:
        """요구사항 ID로 문서 목록 조회"""
        pass
    
    @abstractmethod
    def update(self, document: Document) -> Document:
        """문서 업데이트"""
        pass

