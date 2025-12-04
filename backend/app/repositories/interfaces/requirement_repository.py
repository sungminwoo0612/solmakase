"""
요구사항 리포지토리 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.entities.requirement import Requirement


class IRequirementRepository(ABC):
    """
    요구사항 리포지토리 인터페이스
    """
    
    @abstractmethod
    def create(self, requirement: Requirement) -> Requirement:
        """요구사항 생성"""
        pass
    
    @abstractmethod
    def get_by_id(self, requirement_id: UUID) -> Optional[Requirement]:
        """ID로 요구사항 조회"""
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> List[Requirement]:
        """사용자 ID로 요구사항 목록 조회"""
        pass
    
    @abstractmethod
    def update(self, requirement: Requirement) -> Requirement:
        """요구사항 업데이트"""
        pass
    
    @abstractmethod
    def delete(self, requirement_id: UUID) -> bool:
        """요구사항 삭제"""
        pass

