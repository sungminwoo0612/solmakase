"""
배포 ORM 모델
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
import uuid

from app.db.base import Base
from app.db.types import GUID


class DeploymentModel(Base):
    """
    배포 ORM 모델
    """
    __tablename__ = "deployments"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    infrastructure_design_id = Column(GUID(), ForeignKey("infrastructure_designs.id"), nullable=False)
    iac_code_id = Column(GUID(), ForeignKey("iac_codes.id"), nullable=False)
    status = Column(String(50), default="pending")
    deployment_log = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

