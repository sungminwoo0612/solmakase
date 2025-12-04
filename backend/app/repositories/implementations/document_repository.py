"""
문서 리포지토리 구현체
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.interfaces.document_repository import IDocumentRepository
from app.domain.entities.document import Document
from app.models.document import DocumentModel


class DocumentRepository(IDocumentRepository):
    """
    문서 리포지토리 구현체
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, document: Document) -> Document:
        """문서 생성"""
        db_document = DocumentModel(**document.dict())
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return self._to_entity(db_document)
    
    def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """ID로 문서 조회"""
        db_document = self.db.query(DocumentModel).filter(
            DocumentModel.id == document_id
        ).first()
        return self._to_entity(db_document) if db_document else None
    
    def get_by_requirement_id(self, requirement_id: UUID) -> List[Document]:
        """요구사항 ID로 문서 목록 조회"""
        db_documents = self.db.query(DocumentModel).filter(
            DocumentModel.requirement_id == requirement_id
        ).all()
        return [self._to_entity(doc) for doc in db_documents]
    
    def update(self, document: Document) -> Document:
        """문서 업데이트"""
        db_document = self.db.query(DocumentModel).filter(
            DocumentModel.id == document.id
        ).first()
        
        if db_document:
            for key, value in document.dict().items():
                setattr(db_document, key, value)
            self.db.commit()
            self.db.refresh(db_document)
            return self._to_entity(db_document)
        raise ValueError(f"Document {document.id} not found")
    
    def _to_entity(self, db_model: DocumentModel) -> Document:
        """ORM 모델을 도메인 엔티티로 변환"""
        return Document(**db_model.__dict__)

