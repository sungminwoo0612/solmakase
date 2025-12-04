"""
애플리케이션 설정
"""
from pydantic_settings import BaseSettings
from typing import List, Union
import os


class Settings(BaseSettings):
    # 애플리케이션
    APP_NAME: str = "Solmakase"
    DEBUG: bool = False
    
    # 데이터베이스
    DATABASE_URL: str = "sqlite:///./solmakase.db"  # 개발 환경용 SQLite (프로덕션에서는 PostgreSQL 사용)
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 보안
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins를 리스트로 변환"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    # 파일 업로드
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "pptx", "hwp"]
    UPLOAD_DIR: str = "./uploads"
    
    # LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    LLM_TIMEOUT: int = 300  # 5분
    
    # 문서 보관
    DOCUMENT_RETENTION_DAYS: int = 7
    
    # 배포
    DEPLOYMENT_TIMEOUT: int = 1800  # 30분
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

