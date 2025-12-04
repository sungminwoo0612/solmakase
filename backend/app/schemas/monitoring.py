"""
모니터링 스키마 (Pydantic)
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class MonitoringMetric(BaseModel):
    """모니터링 메트릭"""
    name: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime
    tags: Optional[Dict[str, str]] = None


class MonitoringResponse(BaseModel):
    """모니터링 응답 스키마"""
    deployment_id: UUID
    metrics: List[MonitoringMetric]
    status: str  # 'healthy', 'warning', 'critical'
    last_updated: datetime
    
    class Config:
        from_attributes = True


class HealthCheckResponse(BaseModel):
    """헬스 체크 응답"""
    status: str  # 'healthy', 'unhealthy'
    services: Dict[str, str]  # 서비스별 상태
    timestamp: datetime

