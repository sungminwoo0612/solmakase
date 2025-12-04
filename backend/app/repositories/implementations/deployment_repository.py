"""
배포 리포지토리 구현체
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.interfaces.deployment_repository import IDeploymentRepository
from app.domain.entities.deployment import Deployment
from app.models.deployment import DeploymentModel


class DeploymentRepository(IDeploymentRepository):
    """
    배포 리포지토리 구현체
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, deployment: Deployment) -> Deployment:
        """배포 생성"""
        db_deployment = DeploymentModel(**deployment.dict())
        self.db.add(db_deployment)
        self.db.commit()
        self.db.refresh(db_deployment)
        return self._to_entity(db_deployment)
    
    def get_by_id(self, deployment_id: UUID) -> Optional[Deployment]:
        """ID로 배포 조회"""
        db_deployment = self.db.query(DeploymentModel).filter(
            DeploymentModel.id == deployment_id
        ).first()
        return self._to_entity(db_deployment) if db_deployment else None
    
    def get_by_infrastructure_id(self, infrastructure_id: UUID) -> List[Deployment]:
        """인프라 설계 ID로 배포 목록 조회"""
        db_deployments = self.db.query(DeploymentModel).filter(
            DeploymentModel.infrastructure_design_id == infrastructure_id
        ).all()
        return [self._to_entity(dep) for dep in db_deployments]
    
    def update(self, deployment: Deployment) -> Deployment:
        """배포 업데이트"""
        db_deployment = self.db.query(DeploymentModel).filter(
            DeploymentModel.id == deployment.id
        ).first()
        
        if db_deployment:
            for key, value in deployment.dict().items():
                setattr(db_deployment, key, value)
            self.db.commit()
            self.db.refresh(db_deployment)
            return self._to_entity(db_deployment)
        raise ValueError(f"Deployment {deployment.id} not found")
    
    def _to_entity(self, db_model: DeploymentModel) -> Deployment:
        """ORM 모델을 도메인 엔티티로 변환
        
        SQLAlchemy 내부 상태(_sa_instance_state 등)를 제거하고,
        도메인 엔티티에서 정의한 필드만 명시적으로 매핑한다.
        """
        if db_model is None:
            return None
        
        return Deployment(
            id=db_model.id,
            infrastructure_design_id=db_model.infrastructure_design_id,
            iac_code_id=db_model.iac_code_id,
            status=db_model.status,
            deployment_log=db_model.deployment_log,
            started_at=db_model.started_at,
            completed_at=db_model.completed_at,
            created_at=db_model.created_at,
        )

