"""
분석 결과 스키마 (Pydantic)
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime


class AnalysisResult(BaseModel):
    """분석 결과 스키마"""
    requirement_id: UUID
    analysis_data: Dict[str, Any]
    status: str  # 'pending', 'analyzing', 'completed', 'failed'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AnalysisRequest(BaseModel):
    """분석 요청 스키마"""
    requirement_id: UUID


class AnalysisResponse(BaseModel):
    """분석 응답 스키마"""
    requirement_id: UUID
    analysis_data: Dict[str, Any]
    status: str
    created_at: Optional[datetime] = None

