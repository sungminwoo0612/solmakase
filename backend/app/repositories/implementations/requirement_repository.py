"""
요구사항 리포지토리 구현체
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.interfaces.requirement_repository import IRequirementRepository
from app.domain.entities.requirement import Requirement
from app.models.requirement import RequirementModel


class RequirementRepository(IRequirementRepository):
    """
    요구사항 리포지토리 구현체
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, requirement: Requirement) -> Requirement:
        """요구사항 생성"""
        db_requirement = RequirementModel(**requirement.dict())
        self.db.add(db_requirement)
        self.db.commit()
        self.db.refresh(db_requirement)
        return self._to_entity(db_requirement)
    
    def get_by_id(self, requirement_id: UUID) -> Optional[Requirement]:
        """ID로 요구사항 조회"""
        db_requirement = self.db.query(RequirementModel).filter(
            RequirementModel.id == requirement_id
        ).first()
        return self._to_entity(db_requirement) if db_requirement else None
    
    def get_by_user_id(self, user_id: UUID) -> List[Requirement]:
        """사용자 ID로 요구사항 목록 조회"""
        db_requirements = self.db.query(RequirementModel).filter(
            RequirementModel.user_id == user_id
        ).all()
        return [self._to_entity(req) for req in db_requirements]
    
    def update(self, requirement: Requirement) -> Requirement:
        """요구사항 업데이트"""
        db_requirement = self.db.query(RequirementModel).filter(
            RequirementModel.id == requirement.id
        ).first()
        
        if db_requirement:
            for key, value in requirement.dict().items():
                setattr(db_requirement, key, value)
            self.db.commit()
            self.db.refresh(db_requirement)
            return self._to_entity(db_requirement)
        raise ValueError(f"Requirement {requirement.id} not found")
    
    def delete(self, requirement_id: UUID) -> bool:
        """요구사항 삭제"""
        db_requirement = self.db.query(RequirementModel).filter(
            RequirementModel.id == requirement_id
        ).first()
        
        if db_requirement:
            self.db.delete(db_requirement)
            self.db.commit()
            return True
        return False
    
    def _to_entity(self, db_model: RequirementModel) -> Requirement:
        """ORM 모델을 도메인 엔티티로 변환

        SQLAlchemy 내부 상태(_sa_instance_state 등)를 제거하고,
        도메인 엔티티에서 정의한 필드만 명시적으로 매핑한다.
        """
        return Requirement(
            id=db_model.id,
            user_id=db_model.user_id,
            input_type=db_model.input_type,
            service_type=db_model.service_type,
            deployment_type=db_model.deployment_type,
            scale=db_model.scale,
            budget=float(db_model.budget) if db_model.budget is not None else None,
            has_ops_team=bool(db_model.has_ops_team) if db_model.has_ops_team is not None else None,
            special_requirements=db_model.special_requirements,
            structured_data=db_model.structured_data,
            status=db_model.status,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )

