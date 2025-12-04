"""
인프라 설계 ORM 모델
"""
from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
import uuid

from app.db.base import Base
from app.db.types import GUID


class InfrastructureModel(Base):
    """
    인프라 설계 ORM 모델
    """
    __tablename__ = "infrastructure_designs"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(GUID(), ForeignKey("requirements.id"), nullable=False)
    design_type = Column(String(50), nullable=False)
    provider = Column(String(50))
    architecture = Column(JSON, nullable=False)
    cost_estimate = Column(JSON)
    plan_document = Column(Text)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

