"""
FastAPI 애플리케이션 진입점
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import requirements, analysis, infrastructure, deployment, monitoring

app = FastAPI(
    title="Solmakase API",
    description="AI 기반 인프라 아키텍처 자동화 서비스",
    version="1.0.0",
)

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


@app.get("/")
async def root():
    return {"message": "Solmakase API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 실행 방법:
# 1. backend/ 디렉토리에서: uvicorn main:app --reload --host 0.0.0.0 --port 8000
# 2. 프로젝트 루트에서: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
