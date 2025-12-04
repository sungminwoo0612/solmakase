"""
요구사항 수집 API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.schemas.requirement import RequirementCreate, RequirementResponse
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services.requirement_service import RequirementService
from app.core.dependencies import get_requirement_repository, get_chat_repository, get_db
from app.repositories.interfaces.requirement_repository import IRequirementRepository
from app.repositories.interfaces.chat_repository import IChatRepository
from app.repositories.interfaces.document_repository import IDocumentRepository
from app.repositories.implementations.document_repository import DocumentRepository

router = APIRouter()


@router.post("/", response_model=RequirementResponse)
async def create_requirement(
    requirement: RequirementCreate,
    repository: IRequirementRepository = Depends(get_requirement_repository)
):
    """
    요구사항 생성 (설문조사, 전문가 모드)
    """
    service = RequirementService(repository)
    return await service.create_requirement(requirement)


@router.post("/upload")
async def upload_document(
    requirement_id: UUID,
    file: UploadFile = File(...),
    repository: IRequirementRepository = Depends(get_requirement_repository),
    db: Session = Depends(get_db)
):
    """
    문서 업로드
    """
    document_repository: IDocumentRepository = DocumentRepository(db)
    service = RequirementService(repository, document_repository)
    return await service.upload_document(requirement_id, file)


@router.get("/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(
    requirement_id: UUID,
    repository: IRequirementRepository = Depends(get_requirement_repository)
):
    """
    요구사항 조회
    """
    service = RequirementService(repository)
    requirement = await service.get_requirement(requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement


@router.get("/user/{user_id}", response_model=List[RequirementResponse])
async def get_user_requirements(
    user_id: UUID,
    repository: IRequirementRepository = Depends(get_requirement_repository)
):
    """
    사용자의 요구사항 목록 조회
    """
    service = RequirementService(repository)
    return await service.get_user_requirements(user_id)


@router.post("/{requirement_id}/chat", response_model=ChatMessageResponse)
async def create_chat_message(
    requirement_id: UUID,
    chat_message: ChatMessageCreate,
    chat_repository: IChatRepository = Depends(get_chat_repository)
):
    """
    채팅 메시지 생성
    """
    from app.domain.entities.chat_message import ChatMessage
    
    if chat_message.requirement_id != requirement_id:
        raise HTTPException(status_code=400, detail="Requirement ID mismatch")
    
    message = ChatMessage(
        requirement_id=chat_message.requirement_id,
        role=chat_message.role,
        message=chat_message.message,
    )
    
    created = chat_repository.create(message)
    return ChatMessageResponse.from_entity(created)


@router.get("/{requirement_id}/chat", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    requirement_id: UUID,
    chat_repository: IChatRepository = Depends(get_chat_repository)
):
    """
    요구사항의 채팅 메시지 목록 조회
    """
    messages = chat_repository.get_by_requirement_id(requirement_id)
    return [ChatMessageResponse.from_entity(msg) for msg in messages]

