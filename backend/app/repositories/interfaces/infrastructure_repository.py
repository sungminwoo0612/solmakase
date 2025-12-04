"""
인프라 설계 리포지토리 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.entities.infrastructure import Infrastructure


class IInfrastructureRepository(ABC):
    """
    인프라 설계 리포지토리 인터페이스
    """
    
    @abstractmethod
    def create(self, infrastructure: Infrastructure) -> Infrastructure:
        """인프라 설계 생성"""
        pass
    
    @abstractmethod
    def get_by_id(self, infrastructure_id: UUID) -> Optional[Infrastructure]:
        """ID로 인프라 설계 조회"""
        pass
    
    @abstractmethod
    def get_by_requirement_id(self, requirement_id: UUID) -> List[Infrastructure]:
        """요구사항 ID로 인프라 설계 목록 조회"""
        pass
    
    @abstractmethod
    def update(self, infrastructure: Infrastructure) -> Infrastructure:
        """인프라 설계 업데이트"""
        pass

