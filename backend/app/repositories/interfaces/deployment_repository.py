"""
배포 리포지토리 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.entities.deployment import Deployment


class IDeploymentRepository(ABC):
    """
    배포 리포지토리 인터페이스
    """
    
    @abstractmethod
    def create(self, deployment: Deployment) -> Deployment:
        """배포 생성"""
        pass
    
    @abstractmethod
    def get_by_id(self, deployment_id: UUID) -> Optional[Deployment]:
        """ID로 배포 조회"""
        pass
    
    @abstractmethod
    def get_by_infrastructure_id(self, infrastructure_id: UUID) -> List[Deployment]:
        """인프라 설계 ID로 배포 목록 조회"""
        pass
    
    @abstractmethod
    def update(self, deployment: Deployment) -> Deployment:
        """배포 업데이트"""
        pass

