"""
요구사항 ORM 모델
"""
from sqlalchemy import Column, String, Numeric, Boolean, Text, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
import uuid

from app.db.base import Base
from app.db.types import GUID


class RequirementModel(Base):
    """
    요구사항 ORM 모델
    """
    __tablename__ = "requirements"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    input_type = Column(String(50), nullable=False)
    service_type = Column(String(100))
    deployment_type = Column(String(50))
    scale = Column(String(50))
    budget = Column(Numeric(15, 2))
    has_ops_team = Column(Boolean)
    special_requirements = Column(Text)
    structured_data = Column(JSON)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

