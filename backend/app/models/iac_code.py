"""
IaC 코드 ORM 모델
"""
from sqlalchemy import Column, String, Integer, Text, JSON, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
import uuid

from app.db.base import Base
from app.db.types import GUID


class IaCCodeModel(Base):
    """
    IaC 코드 ORM 모델
    """
    __tablename__ = "iac_codes"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    infrastructure_design_id = Column(GUID(), ForeignKey("infrastructure_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    iac_tool = Column(String(50), nullable=False)  # 'terraform', 'ansible', 'kubernetes'
    version = Column(Integer, nullable=False, default=1)
    code_content = Column(Text, nullable=False)
    validation_status = Column(String(50), default="pending")  # 'pending', 'valid', 'invalid'
    validation_errors = Column(JSON)
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100))  # 'system', 'user_prompt'

