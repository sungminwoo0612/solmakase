"""
FastAPI 애플리케이션 진입점
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware
from app.api.v1 import requirements, analysis, infrastructure, deployment, monitoring
from app.db.session import engine, database_url
from app.db.base import Base

# 로깅 설정 초기화
setup_logging()
logger = get_logger("app.main")

app = FastAPI(
    title="Solmakase API",
    description="AI 기반 인프라 아키텍처 자동화 서비스",
    version="1.0.0",
)

# 요청/응답 로깅 미들웨어 (CORS보다 먼저 등록)
app.add_middleware(RequestLoggingMiddleware)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(requirements.router, prefix="/api/v1/requirements", tags=["requirements"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(infrastructure.router, prefix="/api/v1/infrastructure", tags=["infrastructure"])
app.include_router(deployment.router, prefix="/api/v1/deployment", tags=["deployment"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])


@app.on_event("startup")
async def init_db() -> None:
    """
    개발 환경에서 SQLite를 사용할 때 스키마가 꼬여 있는 경우를 방지하기 위해
    테이블을 드롭 후 재생성한다.
    (운영 환경 / PostgreSQL에서는 Alembic 마이그레이션을 사용해야 함)
    """
    try:
        # 모델 모듈을 명시적으로 import 해야 Base.metadata에 테이블이 등록됨
        from app import models  # noqa: F401

        # 개발용 SQLite인 경우, 기존 스키마를 제거하고 다시 만든다.
        if str(database_url).startswith("sqlite"):
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            logger.info("SQLite 데이터베이스 스키마 초기화 완료")
    except Exception as exc:  # pragma: no cover - 로깅 용도
        # DB 초기화 실패 시 애플리케이션이 죽지 않도록 하고, 로그만 남김
        logger.error(f"데이터베이스 초기화 실패: {exc}", exc_info=True)


@app.get("/")
async def root():
    return {"message": "Solmakase API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

