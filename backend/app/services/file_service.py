"""
파일 서비스 (문서 업로드 및 파싱)
"""
from fastapi import UploadFile
from typing import Dict, Any
import os

from app.core.config import settings


class FileService:
    """
    파일 처리 서비스
    """
    
    async def process_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        파일 업로드 및 파싱
        """
        # 파일 검증
        self._validate_file(file)
        
        # 파일 저장
        file_path = await self._save_file(file)
        
        # 파일 파싱
        parsed_data = await self._parse_file(file_path, file.filename)
        
        return parsed_data
    
    def _validate_file(self, file: UploadFile):
        """
        파일 검증
        """
        # 파일 크기 검증
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f"File size exceeds {settings.MAX_UPLOAD_SIZE} bytes")
        
        # 파일 형식 검증
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in settings.ALLOWED_FILE_TYPES:
            raise ValueError(f"File type {file_ext} not allowed")
    
    async def _save_file(self, file: UploadFile) -> str:
        """
        파일 저장
        """
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return file_path
    
    async def _parse_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        파일 파싱 (PDF, docx, pptx, 한글)
        """
        file_ext = filename.split(".")[-1].lower()
        
        if file_ext == "pdf":
            return await self._parse_pdf(file_path)
        elif file_ext == "docx":
            return await self._parse_docx(file_path)
        elif file_ext == "pptx":
            return await self._parse_pptx(file_path)
        elif file_ext == "hwp":
            return await self._parse_hwp(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    async def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """PDF 파싱"""
        # TODO: PyPDF2 또는 pdfplumber 구현
        return {"type": "pdf", "text": ""}
    
    async def _parse_docx(self, file_path: str) -> Dict[str, Any]:
        """DOCX 파싱"""
        # TODO: python-docx 구현
        return {"type": "docx", "text": ""}
    
    async def _parse_pptx(self, file_path: str) -> Dict[str, Any]:
        """PPTX 파싱"""
        # TODO: python-pptx 구현
        return {"type": "pptx", "text": ""}
    
    async def _parse_hwp(self, file_path: str) -> Dict[str, Any]:
        """한글 파일 파싱"""
        # TODO: olefile 또는 pyhwp 구현
        return {"type": "hwp", "text": ""}

