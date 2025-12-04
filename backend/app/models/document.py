"""
문서 ORM 모델
"""
from sqlalchemy import Column, String, BigInteger, Text, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
import uuid

from app.db.base import Base
from app.db.types import GUID


class DocumentModel(Base):
    """
    문서 ORM 모델
    """
    __tablename__ = "documents"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(GUID(), ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'pdf', 'docx', 'pptx', 'hwp'
    file_size = Column(BigInteger, nullable=False)
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text)
    parsed_data = Column(JSON)  # 파싱된 구조화 데이터
    status = Column(String(50), default="uploaded")  # 'uploaded', 'parsing', 'parsed', 'failed'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))  # 7일 후 자동 삭제

