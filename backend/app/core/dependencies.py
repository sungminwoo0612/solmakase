"""
FastAPI 의존성 주입
"""
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.interfaces.requirement_repository import IRequirementRepository
from app.repositories.implementations.requirement_repository import RequirementRepository
from app.repositories.interfaces.infrastructure_repository import IInfrastructureRepository
from app.repositories.implementations.infrastructure_repository import InfrastructureRepository
from app.repositories.interfaces.deployment_repository import IDeploymentRepository
from app.repositories.implementations.deployment_repository import DeploymentRepository
from app.repositories.interfaces.chat_repository import IChatRepository
from app.repositories.implementations.chat_repository import ChatRepository
from app.repositories.interfaces.iac_repository import IIaCRepository
from app.repositories.implementations.iac_repository import IaCRepository


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 의존성
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_requirement_repository(
    db: Session = Depends(get_db)
) -> IRequirementRepository:
    """
    요구사항 리포지토리 의존성
    """
    return RequirementRepository(db)


def get_infrastructure_repository(
    db: Session = Depends(get_db)
) -> IInfrastructureRepository:
    """
    인프라 설계 리포지토리 의존성
    """
    return InfrastructureRepository(db)


def get_deployment_repository(
    db: Session = Depends(get_db)
) -> IDeploymentRepository:
    """
    배포 리포지토리 의존성
    """
    return DeploymentRepository(db)


def get_chat_repository(
    db: Session = Depends(get_db)
) -> IChatRepository:
    """
    채팅 메시지 리포지토리 의존성
    """
    return ChatRepository(db)


def get_iac_repository(
    db: Session = Depends(get_db)
) -> IIaCRepository:
    """
    IaC 코드 리포지토리 의존성
    """
    return IaCRepository(db)

