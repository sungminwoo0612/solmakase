"""
인프라 설계 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.schemas.infrastructure import InfrastructureCreate, InfrastructureResponse
from app.schemas.iac import IaCCodeResponse, IaCCodeModifyRequest
from app.services.infrastructure_service import InfrastructureService
from app.services.llm_service import LLMService
from app.core.dependencies import (
    get_requirement_repository,
    get_infrastructure_repository,
    get_db
)
from app.repositories.interfaces.iac_repository import IIaCRepository
from app.repositories.implementations.iac_repository import IaCRepository
from app.services.iac_service import IaCService
from app.repositories.interfaces.requirement_repository import IRequirementRepository
from app.repositories.interfaces.infrastructure_repository import IInfrastructureRepository
from app.repositories.interfaces.document_repository import IDocumentRepository
from app.repositories.implementations.document_repository import DocumentRepository

router = APIRouter()


@router.post("/design", response_model=InfrastructureResponse)
async def create_infrastructure_design(
    requirement_id: UUID,
    design_type: str = Query("cloud", description="설계 유형: onprem, cloud, hybrid"),
    requirement_repository: IRequirementRepository = Depends(get_requirement_repository),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    db = Depends(get_db)
):
    """
    인프라 설계 생성
    """
    if design_type not in ["onprem", "cloud", "hybrid"]:
        raise HTTPException(status_code=400, detail="Invalid design_type. Must be: onprem, cloud, hybrid")
    
    # LLM 서비스 초기화
    document_repository: IDocumentRepository = DocumentRepository(db)
    llm_service = LLMService(requirement_repository, document_repository)
    
    # 인프라 설계 서비스
    service = InfrastructureService(
        requirement_repository,
        infrastructure_repository,
        llm_service
    )
    
    try:
        infrastructure = await service.design_infrastructure(requirement_id, design_type)
        return InfrastructureResponse.from_entity(infrastructure)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인프라 설계 생성 실패: {str(e)}")


@router.get("/{infrastructure_id}", response_model=InfrastructureResponse)
async def get_infrastructure(
    infrastructure_id: UUID,
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository)
):
    """
    인프라 설계 조회
    """
    infrastructure = infrastructure_repository.get_by_id(infrastructure_id)
    if not infrastructure:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    return InfrastructureResponse.from_entity(infrastructure)


@router.get("/requirement/{requirement_id}", response_model=List[InfrastructureResponse])
async def get_infrastructures_by_requirement(
    requirement_id: UUID,
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository)
):
    """
    요구사항별 인프라 설계 목록 조회
    """
    infrastructures = infrastructure_repository.get_by_requirement_id(requirement_id)
    return [InfrastructureResponse.from_entity(infra) for infra in infrastructures]


@router.get("/requirement/{requirement_id}/compare")
async def compare_infrastructure_designs(
    requirement_id: UUID,
    requirement_repository: IRequirementRepository = Depends(get_requirement_repository),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    db = Depends(get_db)
):
    """
    온프레미스와 클라우드 설계안 비교
    """
    document_repository: IDocumentRepository = DocumentRepository(db)
    llm_service = LLMService(requirement_repository, document_repository)
    
    service = InfrastructureService(
        requirement_repository,
        infrastructure_repository,
        llm_service
    )
    
    comparison = await service.compare_designs(requirement_id)
    return comparison


@router.post("/{infrastructure_id}/generate-iac", response_model=IaCCodeResponse)
async def generate_iac_code(
    infrastructure_id: UUID,
    iac_tool: str = Query("terraform", description="IaC 도구: terraform, ansible, kubernetes"),
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    db = Depends(get_db)
):
    """
    IaC 코드 생성
    """
    if iac_tool not in ["terraform", "ansible", "kubernetes"]:
        raise HTTPException(status_code=400, detail="Invalid iac_tool. Must be: terraform, ansible, kubernetes")
    
    iac_repository: IIaCRepository = IaCRepository(db)
    
    # LLM 서비스 초기화
    from app.repositories.interfaces.document_repository import IDocumentRepository
    from app.repositories.implementations.document_repository import DocumentRepository
    from app.repositories.interfaces.requirement_repository import IRequirementRepository
    from app.repositories.implementations.requirement_repository import RequirementRepository
    
    requirement_repository: IRequirementRepository = RequirementRepository(db)
    document_repository: IDocumentRepository = DocumentRepository(db)
    llm_service = LLMService(requirement_repository, document_repository)
    
    # IaC 서비스
    service = IaCService(infrastructure_repository, iac_repository, llm_service)
    
    try:
        iac_code = await service.generate_terraform_code(infrastructure_id, iac_tool)
        return IaCCodeResponse.from_entity(iac_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IaC 코드 생성 실패: {str(e)}")


@router.get("/{infrastructure_id}/iac-code", response_model=IaCCodeResponse)
async def get_current_iac_code(
    infrastructure_id: UUID,
    db = Depends(get_db)
):
    """
    현재 버전의 IaC 코드 조회
    """
    iac_repository: IIaCRepository = IaCRepository(db)
    iac_code = iac_repository.get_current_version(infrastructure_id)
    
    if not iac_code:
        raise HTTPException(status_code=404, detail="IaC code not found")
    
    return IaCCodeResponse.from_entity(iac_code)


@router.get("/{infrastructure_id}/iac-code/{version}", response_model=IaCCodeResponse)
async def get_iac_code_by_version(
    infrastructure_id: UUID,
    version: int,
    db = Depends(get_db)
):
    """
    특정 버전의 IaC 코드 조회
    """
    iac_repository: IIaCRepository = IaCRepository(db)
    iac_codes = iac_repository.get_by_infrastructure_id(infrastructure_id)
    
    iac_code = next((code for code in iac_codes if code.version == version), None)
    if not iac_code:
        raise HTTPException(status_code=404, detail=f"IaC code version {version} not found")
    
    return IaCCodeResponse.from_entity(iac_code)


@router.post("/{infrastructure_id}/iac-code/modify", response_model=IaCCodeResponse)
async def modify_iac_code(
    infrastructure_id: UUID,
    modify_request: IaCCodeModifyRequest,
    infrastructure_repository: IInfrastructureRepository = Depends(get_infrastructure_repository),
    db = Depends(get_db)
):
    """
    프롬프트 기반 IaC 코드 수정
    """
    iac_repository: IIaCRepository = IaCRepository(db)
    
    # 현재 버전 가져오기
    current_code = iac_repository.get_current_version(infrastructure_id)
    if not current_code:
        raise HTTPException(status_code=404, detail="Current IaC code not found")
    
    # LLM 서비스 초기화
    from app.repositories.interfaces.document_repository import IDocumentRepository
    from app.repositories.implementations.document_repository import DocumentRepository
    from app.repositories.interfaces.requirement_repository import IRequirementRepository
    from app.repositories.implementations.requirement_repository import RequirementRepository
    
    requirement_repository: IRequirementRepository = RequirementRepository(db)
    document_repository: IDocumentRepository = DocumentRepository(db)
    llm_service = LLMService(requirement_repository, document_repository)
    
    # IaC 서비스
    service = IaCService(infrastructure_repository, iac_repository, llm_service)
    
    try:
        modified_code = await service.modify_code_with_prompt(
            current_code.id,
            modify_request.prompt
        )
        return IaCCodeResponse.from_entity(modified_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"코드 수정 실패: {str(e)}")

