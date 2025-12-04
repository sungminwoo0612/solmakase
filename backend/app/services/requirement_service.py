"""
요구사항 서비스 (비즈니스 로직)
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import UploadFile

from app.repositories.interfaces.requirement_repository import IRequirementRepository
from app.repositories.interfaces.document_repository import IDocumentRepository
from app.schemas.requirement import RequirementCreate, RequirementResponse
from app.domain.entities.requirement import Requirement
from app.domain.entities.document import Document
from app.services.file_service import FileService


class RequirementService:
    """
    요구사항 서비스
    """
    
    def __init__(self, repository: IRequirementRepository, document_repository: Optional[IDocumentRepository] = None):
        self.repository = repository
        self.document_repository = document_repository
        self.file_service = FileService()
    
    async def create_requirement(self, requirement_data: RequirementCreate) -> RequirementResponse:
        """
        요구사항 생성
        """
        requirement = Requirement(
            user_id=requirement_data.user_id,
            input_type=requirement_data.input_type,
            service_type=requirement_data.service_type,
            deployment_type=requirement_data.deployment_type,
            scale=requirement_data.scale,
            budget=requirement_data.budget,
            has_ops_team=requirement_data.has_ops_team,
            special_requirements=requirement_data.special_requirements,
        )
        
        created = self.repository.create(requirement)
        return RequirementResponse.from_entity(created)
    
    async def get_requirement(self, requirement_id: UUID) -> Optional[RequirementResponse]:
        """
        요구사항 조회
        """
        requirement = self.repository.get_by_id(requirement_id)
        return RequirementResponse.from_entity(requirement) if requirement else None
    
    async def get_user_requirements(self, user_id: UUID) -> List[RequirementResponse]:
        """
        사용자의 요구사항 목록 조회
        """
        requirements = self.repository.get_by_user_id(user_id)
        return [RequirementResponse.from_entity(req) for req in requirements]
    
    async def upload_document(self, requirement_id: UUID, file: UploadFile) -> dict:
        """
        문서 업로드 및 파싱
        """
        requirement = self.repository.get_by_id(requirement_id)
        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")
        
        if not self.document_repository:
            raise ValueError("Document repository is not initialized")
        
        # 요구사항 상태를 analyzing으로 변경
        requirement.status = "analyzing"
        self.repository.update(requirement)
        
        # 파일 저장 및 파싱
        try:
            parsed_data = await self.file_service.process_file(file)
            
            # 문서 엔티티 생성
            import os
            file_path = parsed_data.get("file_path", "")
            file_size = os.path.getsize(file_path) if file_path and os.path.exists(file_path) else 0
            
            document = Document(
                requirement_id=requirement_id,
                file_name=file.filename or "unknown",
                file_type=parsed_data.get("type", ""),
                file_size=file_size,
                file_path=file_path,
                extracted_text=parsed_data.get("text", ""),
                parsed_data=parsed_data,
                status="parsed",
            )
            
            # 문서 저장
            created_document = self.document_repository.create(document)
            
            # 요구사항의 structured_data 업데이트
            requirement.structured_data = parsed_data
            requirement.status = "completed"
            updated = self.repository.update(requirement)
            
            return {
                "requirement_id": str(updated.id),
                "document_id": str(created_document.id),
                "file_name": file.filename,
                "status": "parsed",
                "parsed_data": parsed_data
            }
        except Exception as e:
            # 에러 발생 시 상태를 failed로 변경
            requirement.status = "failed"
            self.repository.update(requirement)
            raise ValueError(f"문서 처리 실패: {str(e)}")

