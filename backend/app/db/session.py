"""
데이터베이스 세션 관리
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# DATABASE_URL이 비어있거나 유효하지 않은 경우 기본값 사용
database_url = settings.DATABASE_URL or "sqlite:///./solmakase.db"

# SQLite인 경우 connect_args 추가
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=10 if not database_url.startswith("sqlite") else 1,
    max_overflow=20 if not database_url.startswith("sqlite") else 0,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

