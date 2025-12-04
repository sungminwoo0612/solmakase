"""
배포 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from uuid import UUID

from app.schemas.deployment import DeploymentCreate, DeploymentResponse, DeploymentUpdate
from app.services.deployment_service import DeploymentService
from app.core.dependencies import (
    get_deployment_repository,
    get_infrastructure_repository,
    get_iac_repository,
    get_db
)
from app.repositories.interfaces.deployment_repository import IDeploymentRepository
from app.repositories.interfaces.infrastructure_repository import IInfrastructureRepository
from app.repositories.interfaces.iac_repository import IIaCRepository
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger("app.api.deployment")


async def deploy_infrastructure_background(
    deployment_id: UUID,
    deployment_service: DeploymentService,
    iac_repository: IIaCRepository,
    db
):
    """백그라운드에서 인프라 배포 실행"""
    from app.utils.deployment_executor import DeploymentExecutor
    
    try:
        logger.info(f"배포 시작: deployment_id={deployment_id}")
        
        # 배포 시작
        await deployment_service.start_deployment(deployment_id)
        
        # 배포 정보 조회
        deployment = deployment_service.deployment_repository.get_by_id(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        # IaC 코드 조회
        iac_code = iac_repository.get_by_id(deployment.iac_code_id)
        if not iac_code:
            raise ValueError(f"IaC code {deployment.iac_code_id} not found")
        
        # 배포 실행기 생성
        executor = DeploymentExecutor(deployment_id)
        
        # IaC 도구에 따라 실행
        success = False
        log = ""
        
        if iac_code.iac_tool == "terraform":
            success, log = await executor.execute_terraform(iac_code.code_content)
        elif iac_code.iac_tool == "ansible":
            success, log = await executor.execute_ansible(iac_code.code_content)
        else:
            raise ValueError(f"지원하지 않는 IaC 도구: {iac_code.iac_tool}")
        
        # 배포 완료 처리
        await deployment_service.complete_deployment(
            deployment_id,
            success=success,
            log=log
        )
        
        logger.info(f"배포 완료: deployment_id={deployment_id}, success={success}")
        
    except Exception as e:
        logger.exception(f"배포 중 에러 발생: deployment_id={deployment_id}, error={str(e)}")
        try:
            await deployment_service.complete_deployment(
                deployment_id,
                success=False,
                log=f"배포 실패: {str(e)}"
            )
        except Exception as update_error:
            logger.error(f"배포 상태 업데이트 실패: deployment_id={deployment_id}, error={str(update_error)}")


@router.post("/", response_model=DeploymentResponse)
async def create_deployment(
    deployment_data: DeploymentCreate,
    background_tasks: BackgroundTasks,
    deployment_repository: IDeploymentRepository = Depends(get_deployment_repository),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    iac_repository: IIaCRepository = Depends(get_iac_repository),
    db = Depends(get_db)
):
    """
    배포 생성 및 시작
    
    - 인프라 설계와 IaC 코드를 기반으로 배포 생성
    - 백그라운드에서 배포 실행
    """
    service = DeploymentService(
        deployment_repository,
        infrastructure_repository,
        iac_repository
    )
    
    # 배포 생성
    deployment = await service.create_deployment(deployment_data)
    
    # 백그라운드에서 배포 실행
    background_tasks.add_task(
        deploy_infrastructure_background,
        deployment.id,
        service,
        iac_repository,
        db
    )
    
    logger.info(f"배포 작업 시작: deployment_id={deployment.id}")
    
    return deployment


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: UUID,
    deployment_repository: IDeploymentRepository = Depends(get_deployment_repository),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    iac_repository: IIaCRepository = Depends(get_iac_repository)
):
    """
    배포 조회
    """
    service = DeploymentService(
        deployment_repository,
        infrastructure_repository,
        iac_repository
    )
    
    deployment = await service.get_deployment(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return deployment


@router.get("/infrastructure/{infrastructure_id}", response_model=List[DeploymentResponse])
async def get_deployments_by_infrastructure(
    infrastructure_id: UUID,
    deployment_repository: IDeploymentRepository = Depends(get_deployment_repository),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    iac_repository: IIaCRepository = Depends(get_iac_repository)
):
    """
    인프라 설계 ID로 배포 목록 조회
    """
    service = DeploymentService(
        deployment_repository,
        infrastructure_repository,
        iac_repository
    )
    
    return await service.get_deployments_by_infrastructure(infrastructure_id)


@router.patch("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: UUID,
    update_data: DeploymentUpdate,
    deployment_repository: IDeploymentRepository = Depends(get_deployment_repository),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    iac_repository: IIaCRepository = Depends(get_iac_repository)
):
    """
    배포 업데이트
    """
    service = DeploymentService(
        deployment_repository,
        infrastructure_repository,
        iac_repository
    )
    
    try:
        return await service.update_deployment(deployment_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{deployment_id}/start", response_model=DeploymentResponse)
async def start_deployment(
    deployment_id: UUID,
    deployment_repository: IDeploymentRepository = Depends(get_deployment_repository),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    iac_repository: IIaCRepository = Depends(get_iac_repository)
):
    """
    배포 시작
    """
    service = DeploymentService(
        deployment_repository,
        infrastructure_repository,
        iac_repository
    )
    
    try:
        return await service.start_deployment(deployment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[DeploymentResponse])
async def list_deployments(
    infrastructure_id: Optional[UUID] = Query(None, description="인프라 설계 ID로 필터링"),
    status: Optional[str] = Query(None, description="상태로 필터링"),
    deployment_repository: IDeploymentRepository = Depends(get_deployment_repository),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    iac_repository: IIaCRepository = Depends(get_iac_repository)
):
    """
    배포 목록 조회
    
    - 인프라 설계 ID로 필터링 가능
    - 상태로 필터링 가능
    """
    service = DeploymentService(
        deployment_repository,
        infrastructure_repository,
        iac_repository
    )
    
    if infrastructure_id:
        deployments = await service.get_deployments_by_infrastructure(infrastructure_id)
    else:
        # 모든 배포 조회 (리포지토리에 메서드 추가 필요)
        # 임시로 빈 리스트 반환
        deployments = []
    
    # 상태 필터링
    if status:
        deployments = [d for d in deployments if d.status == status]
    
    return deployments


@router.post("/{deployment_id}/rollback", response_model=DeploymentResponse)
async def rollback_deployment(
    deployment_id: UUID,
    background_tasks: BackgroundTasks,
    deployment_repository: IDeploymentRepository = Depends(get_deployment_repository),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    iac_repository: IIaCRepository = Depends(get_iac_repository),
    db = Depends(get_db)
):
    """
    배포 롤백
    
    - 배포된 인프라를 제거하거나 이전 상태로 복원
    - 백그라운드에서 롤백 실행
    """
    from app.utils.deployment_executor import DeploymentExecutor
    
    service = DeploymentService(
        deployment_repository,
        infrastructure_repository,
        iac_repository
    )
    
    try:
        # 롤백 시작
        deployment = await service.rollback_deployment(deployment_id)
        
        # 배포 정보 조회
        deployment_entity = service.deployment_repository.get_by_id(deployment_id)
        if not deployment_entity:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        # IaC 코드 조회
        iac_code = iac_repository.get_by_id(deployment_entity.iac_code_id)
        if not iac_code:
            raise HTTPException(status_code=404, detail="IaC code not found")
        
        # 백그라운드에서 롤백 실행
        async def rollback_background():
            try:
                executor = DeploymentExecutor(deployment_id)
                
                if iac_code.iac_tool == "terraform":
                    success, log = await executor.rollback_terraform()
                else:
                    raise ValueError(f"롤백은 Terraform만 지원합니다. 현재 도구: {iac_code.iac_tool}")
                
                # 롤백 결과 업데이트
                if success:
                    await service.update_deployment(
                        deployment_id,
                        DeploymentUpdate(
                            status="rolled_back",
                            deployment_log=log
                        )
                    )
                else:
                    await service.update_deployment(
                        deployment_id,
                        DeploymentUpdate(
                            status="failed",
                            deployment_log=f"롤백 실패: {log}"
                        )
                    )
                
                logger.info(f"롤백 완료: deployment_id={deployment_id}, success={success}")
            except Exception as e:
                logger.exception(f"롤백 중 에러 발생: deployment_id={deployment_id}, error={str(e)}")
                await service.update_deployment(
                    deployment_id,
                    DeploymentUpdate(
                        status="failed",
                        deployment_log=f"롤백 실패: {str(e)}"
                    )
                )
        
        background_tasks.add_task(rollback_background)
        
        return deployment
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
