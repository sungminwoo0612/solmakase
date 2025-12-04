"""
IaC 코드 리포지토리 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.entities.iac_code import IaCCode


class IIaCRepository(ABC):
    """
    IaC 코드 리포지토리 인터페이스
    """
    
    @abstractmethod
    def create(self, iac_code: IaCCode) -> IaCCode:
        """IaC 코드 생성"""
        pass
    
    @abstractmethod
    def get_by_id(self, iac_code_id: UUID) -> Optional[IaCCode]:
        """ID로 IaC 코드 조회"""
        pass
    
    @abstractmethod
    def get_by_infrastructure_id(self, infrastructure_id: UUID) -> List[IaCCode]:
        """인프라 설계 ID로 IaC 코드 목록 조회"""
        pass
    
    @abstractmethod
    def get_current_version(self, infrastructure_id: UUID) -> Optional[IaCCode]:
        """현재 버전의 IaC 코드 조회"""
        pass
    
    @abstractmethod
    def update(self, iac_code: IaCCode) -> IaCCode:
        """IaC 코드 업데이트"""
        pass

