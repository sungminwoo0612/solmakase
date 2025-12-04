"""
인프라 설계 리포지토리 구현체
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.interfaces.infrastructure_repository import IInfrastructureRepository
from app.domain.entities.infrastructure import Infrastructure
from app.models.infrastructure import InfrastructureModel


class InfrastructureRepository(IInfrastructureRepository):
    """
    인프라 설계 리포지토리 구현체
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, infrastructure: Infrastructure) -> Infrastructure:
        """인프라 설계 생성"""
        db_infrastructure = InfrastructureModel(**infrastructure.dict())
        self.db.add(db_infrastructure)
        self.db.commit()
        self.db.refresh(db_infrastructure)
        return self._to_entity(db_infrastructure)
    
    def get_by_id(self, infrastructure_id: UUID) -> Optional[Infrastructure]:
        """ID로 인프라 설계 조회"""
        db_infrastructure = self.db.query(InfrastructureModel).filter(
            InfrastructureModel.id == infrastructure_id
        ).first()
        return self._to_entity(db_infrastructure) if db_infrastructure else None
    
    def get_by_requirement_id(self, requirement_id: UUID) -> List[Infrastructure]:
        """요구사항 ID로 인프라 설계 목록 조회"""
        db_infrastructures = self.db.query(InfrastructureModel).filter(
            InfrastructureModel.requirement_id == requirement_id
        ).all()
        return [self._to_entity(infra) for infra in db_infrastructures]
    
    def update(self, infrastructure: Infrastructure) -> Infrastructure:
        """인프라 설계 업데이트"""
        db_infrastructure = self.db.query(InfrastructureModel).filter(
            InfrastructureModel.id == infrastructure.id
        ).first()
        
        if db_infrastructure:
            for key, value in infrastructure.dict().items():
                setattr(db_infrastructure, key, value)
            self.db.commit()
            self.db.refresh(db_infrastructure)
            return self._to_entity(db_infrastructure)
        raise ValueError(f"Infrastructure {infrastructure.id} not found")
    
    def _to_entity(self, db_model: InfrastructureModel) -> Infrastructure:
        """ORM 모델을 도메인 엔티티로 변환"""
        return Infrastructure(**db_model.__dict__)

