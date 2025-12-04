"""
IaC 코드 리포지토리 구현체
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.interfaces.iac_repository import IIaCRepository
from app.domain.entities.iac_code import IaCCode
from app.models.iac_code import IaCCodeModel


class IaCRepository(IIaCRepository):
    """
    IaC 코드 리포지토리 구현체
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, iac_code: IaCCode) -> IaCCode:
        """IaC 코드 생성"""
        db_iac = IaCCodeModel(**iac_code.dict())
        self.db.add(db_iac)
        self.db.commit()
        self.db.refresh(db_iac)
        return self._to_entity(db_iac)
    
    def get_by_id(self, iac_code_id: UUID) -> Optional[IaCCode]:
        """ID로 IaC 코드 조회"""
        db_iac = self.db.query(IaCCodeModel).filter(
            IaCCodeModel.id == iac_code_id
        ).first()
        return self._to_entity(db_iac) if db_iac else None
    
    def get_by_infrastructure_id(self, infrastructure_id: UUID) -> List[IaCCode]:
        """인프라 설계 ID로 IaC 코드 목록 조회"""
        db_iacs = self.db.query(IaCCodeModel).filter(
            IaCCodeModel.infrastructure_design_id == infrastructure_id
        ).order_by(IaCCodeModel.version.desc()).all()
        return [self._to_entity(iac) for iac in db_iacs]
    
    def get_current_version(self, infrastructure_id: UUID) -> Optional[IaCCode]:
        """현재 버전의 IaC 코드 조회"""
        db_iac = self.db.query(IaCCodeModel).filter(
            IaCCodeModel.infrastructure_design_id == infrastructure_id,
            IaCCodeModel.is_current == True
        ).first()
        return self._to_entity(db_iac) if db_iac else None
    
    def update(self, iac_code: IaCCode) -> IaCCode:
        """IaC 코드 업데이트"""
        db_iac = self.db.query(IaCCodeModel).filter(
            IaCCodeModel.id == iac_code.id
        ).first()
        
        if db_iac:
            for key, value in iac_code.dict().items():
                setattr(db_iac, key, value)
            self.db.commit()
            self.db.refresh(db_iac)
            return self._to_entity(db_iac)
        raise ValueError(f"IaC code {iac_code.id} not found")
    
    def _to_entity(self, db_model: IaCCodeModel) -> IaCCode:
        """ORM 모델을 도메인 엔티티로 변환"""
        return IaCCode(**db_model.__dict__)

