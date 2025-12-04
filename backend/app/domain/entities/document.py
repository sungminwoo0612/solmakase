"""
문서 도메인 엔티티
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


@dataclass
class Document:
    """
    문서 도메인 엔티티
    """
    id: Optional[UUID] = None
    requirement_id: UUID = None
    file_name: str = None
    file_type: str = None  # 'pdf', 'docx', 'pptx', 'hwp'
    file_size: int = None
    file_path: str = None
    extracted_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    status: str = "uploaded"  # 'uploaded', 'parsing', 'parsed', 'failed'
    created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    def dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "requirement_id": self.requirement_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "file_path": self.file_path,
            "extracted_text": self.extracted_text,
            "parsed_data": self.parsed_data,
            "status": self.status,
            "created_at": self.created_at,
            "deleted_at": self.deleted_at,
        }

