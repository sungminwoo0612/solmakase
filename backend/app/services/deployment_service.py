"""
배포 서비스
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.domain.entities.deployment import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentResponse, DeploymentUpdate
from app.repositories.interfaces.deployment_repository import IDeploymentRepository
from app.repositories.interfaces.infrastructure_repository import IInfrastructureRepository
from app.repositories.interfaces.iac_repository import IIaCRepository
from app.core.logging_config import get_logger

logger = get_logger("app.services.deployment")


class DeploymentService:
    """
    배포 서비스
    """
    
    def __init__(
        self,
        deployment_repository: IDeploymentRepository,
        infrastructure_repository: Optional[IInfrastructureRepository] = None,
        iac_repository: Optional[IIaCRepository] = None
    ):
        self.deployment_repository = deployment_repository
        self.infrastructure_repository = infrastructure_repository
        self.iac_repository = iac_repository
    
    async def create_deployment(self, deployment_data: DeploymentCreate) -> DeploymentResponse:
        """
        배포 생성
        
        - 인프라 설계와 IaC 코드가 존재하는지 확인
        - 배포 엔티티 생성 및 저장
        """
        # 인프라 설계 확인
        if self.infrastructure_repository:
            infrastructure = self.infrastructure_repository.get_by_id(
                deployment_data.infrastructure_design_id
            )
            if not infrastructure:
                raise ValueError(f"Infrastructure {deployment_data.infrastructure_design_id} not found")
        
        # IaC 코드 확인
        if self.iac_repository:
            iac_code = self.iac_repository.get_by_id(deployment_data.iac_code_id)
            if not iac_code:
                raise ValueError(f"IaC code {deployment_data.iac_code_id} not found")
        
        # 배포 엔티티 생성
        deployment = Deployment(
            infrastructure_design_id=deployment_data.infrastructure_design_id,
            iac_code_id=deployment_data.iac_code_id,
            status="pending"
        )
        
        # 저장
        created = self.deployment_repository.create(deployment)
        logger.info(f"배포 생성: deployment_id={created.id}, infrastructure_id={deployment_data.infrastructure_design_id}")
        
        return DeploymentResponse.from_entity(created)
    
    async def get_deployment(self, deployment_id: UUID) -> Optional[DeploymentResponse]:
        """
        배포 조회
        """
        deployment = self.deployment_repository.get_by_id(deployment_id)
        return DeploymentResponse.from_entity(deployment) if deployment else None
    
    async def get_deployments_by_infrastructure(
        self,
        infrastructure_id: UUID
    ) -> List[DeploymentResponse]:
        """
        인프라 설계 ID로 배포 목록 조회
        """
        deployments = self.deployment_repository.get_by_infrastructure_id(infrastructure_id)
        return [DeploymentResponse.from_entity(dep) for dep in deployments]
    
    async def update_deployment(
        self,
        deployment_id: UUID,
        update_data: DeploymentUpdate
    ) -> DeploymentResponse:
        """
        배포 업데이트
        """
        deployment = self.deployment_repository.get_by_id(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        # 업데이트할 필드만 적용
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(deployment, key, value)
        
        updated = self.deployment_repository.update(deployment)
        logger.info(f"배포 업데이트: deployment_id={deployment_id}, status={updated.status}")
        
        return DeploymentResponse.from_entity(updated)
    
    async def start_deployment(self, deployment_id: UUID) -> DeploymentResponse:
        """
        배포 시작
        """
        deployment = self.deployment_repository.get_by_id(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        if deployment.status != "pending":
            raise ValueError(f"Deployment {deployment_id} is not in pending status")
        
        deployment.status = "deploying"
        deployment.started_at = datetime.utcnow()
        
        updated = self.deployment_repository.update(deployment)
        logger.info(f"배포 시작: deployment_id={deployment_id}")
        
        return DeploymentResponse.from_entity(updated)
    
    async def complete_deployment(
        self,
        deployment_id: UUID,
        success: bool = True,
        log: Optional[str] = None
    ) -> DeploymentResponse:
        """
        배포 완료
        """
        deployment = self.deployment_repository.get_by_id(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        deployment.status = "success" if success else "failed"
        deployment.completed_at = datetime.utcnow()
        if log:
            deployment.deployment_log = log
        
        updated = self.deployment_repository.update(deployment)
        logger.info(f"배포 완료: deployment_id={deployment_id}, status={updated.status}")
        
        return DeploymentResponse.from_entity(updated)
    
    async def rollback_deployment(self, deployment_id: UUID) -> DeploymentResponse:
        """
        배포 롤백
        
        - 배포된 인프라를 제거하거나 이전 상태로 복원
        """
        deployment = self.deployment_repository.get_by_id(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        # 성공한 배포만 롤백 가능
        if deployment.status != "success":
            raise ValueError(f"롤백은 성공한 배포만 가능합니다. 현재 상태: {deployment.status}")
        
        # 롤백 시작
        deployment.status = "rolled_back"
        deployment.completed_at = datetime.utcnow()
        
        updated = self.deployment_repository.update(deployment)
        logger.info(f"배포 롤백 시작: deployment_id={deployment_id}")
        
        return DeploymentResponse.from_entity(updated)

