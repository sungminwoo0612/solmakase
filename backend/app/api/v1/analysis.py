"""
분석 결과 API
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
from uuid import UUID

from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.llm_service import LLMService
from app.core.dependencies import get_requirement_repository, get_db
from app.core.config import settings
from app.core.logging_config import get_logger
from app.repositories.interfaces.requirement_repository import IRequirementRepository
from app.repositories.interfaces.document_repository import IDocumentRepository
from app.repositories.implementations.document_repository import DocumentRepository

router = APIRouter()
logger = get_logger("app.api.analysis")


async def analyze_requirement_background(
    requirement_id: UUID,
    llm_service: LLMService
):
    """백그라운드에서 요구사항 분석 실행 (타임아웃 포함)"""
    try:
        logger.info(f"분석 시작: requirement_id={requirement_id}")
        
        # 요구사항 상태를 analyzing으로 변경
        requirement = llm_service.requirement_repository.get_by_id(requirement_id)
        if not requirement:
            logger.error(f"요구사항을 찾을 수 없음: requirement_id={requirement_id}")
            return
        
        requirement.status = "analyzing"
        llm_service.requirement_repository.update(requirement)
        logger.info(f"분석 상태 변경: requirement_id={requirement_id}, status=analyzing")
        
        # 타임아웃을 포함한 분석 실행
        try:
            analysis_result = await asyncio.wait_for(
                llm_service.analyze_requirement(requirement_id),
                timeout=settings.LLM_TIMEOUT
            )
            
            # 요구사항 업데이트
            requirement = llm_service.requirement_repository.get_by_id(requirement_id)
            if requirement:
                requirement.structured_data = analysis_result
                requirement.status = "completed"
                llm_service.requirement_repository.update(requirement)
                logger.info(
                    f"분석 완료: requirement_id={requirement_id}, "
                    f"status=completed, "
                    f"data_keys={list(analysis_result.keys()) if analysis_result else []}"
                )
        except asyncio.TimeoutError:
            logger.error(f"분석 타임아웃: requirement_id={requirement_id}, timeout={settings.LLM_TIMEOUT}초")
            requirement = llm_service.requirement_repository.get_by_id(requirement_id)
            if requirement:
                requirement.status = "failed"
                llm_service.requirement_repository.update(requirement)
        except ValueError as ve:
            # LLM 서비스 초기화 실패 (API 키 없음 등)
            error_msg = str(ve)
            logger.error(f"LLM 서비스 초기화 실패: requirement_id={requirement_id}, error={error_msg}")
            requirement = llm_service.requirement_repository.get_by_id(requirement_id)
            if requirement:
                requirement.status = "failed"
                # 에러 메시지를 structured_data에 저장하여 프론트엔드에서 확인 가능하도록
                if not requirement.structured_data:
                    requirement.structured_data = {}
                requirement.structured_data["error"] = error_msg
                llm_service.requirement_repository.update(requirement)
                
    except Exception as e:
        # 예상치 못한 에러 발생 시 상태를 failed로 변경
        logger.exception(f"분석 중 예상치 못한 에러 발생: requirement_id={requirement_id}, error={str(e)}")
        try:
            requirement = llm_service.requirement_repository.get_by_id(requirement_id)
            if requirement:
                requirement.status = "failed"
                llm_service.requirement_repository.update(requirement)
        except Exception as update_error:
            logger.error(f"상태 업데이트 실패: requirement_id={requirement_id}, error={str(update_error)}")


@router.post("/{requirement_id}", response_model=AnalysisResponse)
async def analyze_requirement(
    requirement_id: UUID,
    background_tasks: BackgroundTasks,
    requirement_repository: IRequirementRepository = Depends(get_requirement_repository),
    db = Depends(get_db)
):
    """
    요구사항 분석 실행
    
    - 이미 분석 중이거나 완료된 경우 재실행하지 않음
    - LLM API 키가 없으면 즉시 실패 처리
    """
    from sqlalchemy.orm import Session
    
    # 요구사항 확인
    requirement = requirement_repository.get_by_id(requirement_id)
    if not requirement:
        logger.warning(f"요구사항을 찾을 수 없음: requirement_id={requirement_id}")
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # 이미 분석 중이거나 완료된 경우
    if requirement.status in ["analyzing", "completed"]:
        logger.info(f"이미 분석 중이거나 완료됨: requirement_id={requirement_id}, status={requirement.status}")
        return AnalysisResponse(
            requirement_id=requirement_id,
            analysis_data=requirement.structured_data or {},
            status=requirement.status,
            created_at=requirement.updated_at or requirement.created_at
        )
    
    # LLM API 키 확인
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY가 설정되지 않음")
        requirement.status = "failed"
        requirement_repository.update(requirement)
        raise HTTPException(
            status_code=503,
            detail="LLM 서비스가 사용 불가능합니다. OPENAI_API_KEY를 설정해주세요."
        )
    
    # LLM 서비스 초기화
    document_repository: IDocumentRepository = DocumentRepository(db)
    llm_service = LLMService(requirement_repository, document_repository)
    
    # 백그라운드에서 분석 실행
    background_tasks.add_task(
        analyze_requirement_background,
        requirement_id,
        llm_service
    )
    
    logger.info(f"분석 작업 시작: requirement_id={requirement_id}")
    
    return AnalysisResponse(
        requirement_id=requirement_id,
        analysis_data={},
        status="analyzing",
        created_at=requirement.created_at
    )


@router.get("/{requirement_id}", response_model=AnalysisResponse)
async def get_analysis_result(
    requirement_id: UUID,
    requirement_repository: IRequirementRepository = Depends(get_requirement_repository)
):
    """
    분석 결과 조회
    
    - 실시간으로 분석 상태와 결과를 반환
    - 분석 중이어도 기존에 저장된 부분 결과가 있으면 반환
    """
    requirement = requirement_repository.get_by_id(requirement_id)
    if not requirement:
        logger.warning(f"요구사항을 찾을 수 없음: requirement_id={requirement_id}")
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    analysis_data = requirement.structured_data or {}
    
    # 로깅 (디버깅용)
    logger.debug(
        f"분석 결과 조회: requirement_id={requirement_id}, "
        f"status={requirement.status}, "
        f"data_keys={list(analysis_data.keys()) if analysis_data else []}"
    )
    
    return AnalysisResponse(
        requirement_id=requirement_id,
        analysis_data=analysis_data,
        status=requirement.status,
        created_at=requirement.updated_at or requirement.created_at
    )

