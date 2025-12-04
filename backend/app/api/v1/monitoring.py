"""
모니터링 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.schemas.monitoring import MonitoringResponse, MonitoringMetric, HealthCheckResponse
from app.core.dependencies import get_deployment_repository, get_db
from app.repositories.interfaces.deployment_repository import IDeploymentRepository
from app.core.logging_config import get_logger
from app.utils.metrics_collector import MetricsCollector
from app.utils.vm_connectivity import VMConnectivityChecker

router = APIRouter()
logger = get_logger("app.api.monitoring")


@router.get("/deployment/{deployment_id}", response_model=MonitoringResponse)
async def get_deployment_monitoring(
    deployment_id: UUID,
    deployment_repository: IDeploymentRepository = Depends(get_deployment_repository),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간")
):
    """
    배포 모니터링 데이터 조회
    
    - 배포된 인프라의 메트릭 수집
    - CPU, 메모리, 네트워크, 디스크 등 모니터링
    """
    # 배포 확인
    deployment = deployment_repository.get_by_id(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # 기본 시간 범위 설정 (최근 1시간)
    if not end_time:
        end_time = datetime.utcnow()
    if not start_time:
        start_time = end_time - timedelta(hours=1)
    
    # 메트릭 수집기로 데이터 수집
    collector = MetricsCollector(deployment_id)
    metrics_data = await collector.collect_metrics(start_time, end_time)
    
    # 최신 메트릭만 반환 (또는 집계된 메트릭)
    latest_metrics = {}
    for metric_data in metrics_data:
        name = metric_data["name"]
        if name not in latest_metrics or metric_data["timestamp"] > latest_metrics[name]["timestamp"]:
            latest_metrics[name] = metric_data
    
    # MonitoringMetric 객체로 변환
    metrics = [
        MonitoringMetric(
            name=m["name"],
            value=m["value"],
            unit=m.get("unit"),
            timestamp=m["timestamp"],
            tags=m.get("tags")
        )
        for m in latest_metrics.values()
    ]
    
    # 상태 결정
    status = "healthy"
    if any(m.value > 80 for m in metrics if m.unit == "percent"):
        status = "warning"
    if any(m.value > 95 for m in metrics if m.unit == "percent"):
        status = "critical"
    
    logger.info(f"모니터링 데이터 조회: deployment_id={deployment_id}, metrics_count={len(metrics)}")
    
    return MonitoringResponse(
        deployment_id=deployment_id,
        metrics=metrics,
        status=status,
        last_updated=datetime.utcnow()
    )


@router.get("/deployment/{deployment_id}/metrics/{metric_name}", response_model=List[MonitoringMetric])
async def get_metric(
    deployment_id: UUID,
    metric_name: str,
    deployment_repository: IDeploymentRepository = Depends(get_deployment_repository),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간")
):
    """
    특정 메트릭 조회
    
    - 특정 메트릭의 시계열 데이터 반환
    """
    # 배포 확인
    deployment = deployment_repository.get_by_id(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # 기본 시간 범위 설정
    if not end_time:
        end_time = datetime.utcnow()
    if not start_time:
        start_time = end_time - timedelta(hours=1)
    
    # 메트릭 수집기로 데이터 수집
    collector = MetricsCollector(deployment_id)
    metrics_data = await collector.collect_metric_by_name(metric_name, start_time, end_time)
    
    # MonitoringMetric 객체로 변환
    metrics = [
        MonitoringMetric(
            name=m["name"],
            value=m["value"],
            unit=m.get("unit"),
            timestamp=m["timestamp"],
            tags=m.get("tags")
        )
        for m in metrics_data
    ]
    
    logger.info(f"메트릭 조회: deployment_id={deployment_id}, metric_name={metric_name}, count={len(metrics)}")
    
    return metrics


@router.get("/vm/connectivity")
async def check_vm_connectivity(
    vm_name: Optional[str] = Query(None, description="VM 이름 (기본값: Solmakase-Dev-Server)"),
    vagrant_dir: Optional[str] = Query(None, description="Vagrantfile 디렉토리")
):
    """
    VM 연결성 확인
    
    - VirtualBox VM 상태 확인
    - Vagrant 상태 확인
    - SSH 연결 확인
    - 네트워크 연결 확인
    """
    checker = VMConnectivityChecker(vm_name=vm_name)
    results = await checker.check_all(vagrant_dir=vagrant_dir)
    
    logger.info(f"VM 연결성 확인: overall_status={results['overall']['status']}")
    
    return results


@router.get("/vm/virtualbox")
async def check_virtualbox_status(
    vm_name: Optional[str] = Query(None, description="VM 이름")
):
    """
    VirtualBox VM 상태 확인
    """
    checker = VMConnectivityChecker(vm_name=vm_name)
    result = await checker.check_virtualbox_vm_status()
    
    return result


@router.get("/vm/vagrant")
async def check_vagrant_status(
    vagrant_dir: Optional[str] = Query(None, description="Vagrantfile 디렉토리")
):
    """
    Vagrant 상태 확인
    """
    checker = VMConnectivityChecker()
    result = await checker.check_vagrant_status(vagrant_dir=vagrant_dir)
    
    return result


@router.get("/vm/ssh")
async def check_ssh_connection(
    host: str = Query("localhost", description="호스트 주소"),
    port: int = Query(22, description="SSH 포트"),
    vagrant_dir: Optional[str] = Query(None, description="Vagrantfile 디렉토리 (Vagrant SSH 확인 시)")
):
    """
    SSH 연결 확인
    
    - 직접 호스트/포트 지정 또는
    - Vagrant SSH 설정 사용
    """
    checker = VMConnectivityChecker()
    
    if vagrant_dir:
        result = await checker.check_vagrant_ssh(vagrant_dir=vagrant_dir)
    else:
        result = await checker.check_ssh_connection(host=host, port=port)
    
    return result


@router.get("/vm/network")
async def check_network_connectivity(
    include_optional: bool = Query(True, description="선택적 서비스(PostgreSQL, Redis) 포함 여부")
):
    """
    네트워크 연결 확인
    
    - 기본 서비스 포트 연결 확인
    - 필수 서비스(FastAPI)와 선택적 서비스(PostgreSQL, Redis) 구분
    """
    checker = VMConnectivityChecker()
    
    # 기본 호스트 리스트
    hosts = [
        ("localhost", 8000),  # FastAPI (필수)
        ("localhost", 5173),  # Vite (선택적)
    ]
    
    if include_optional:
        hosts.extend([
            ("localhost", 5432),  # PostgreSQL (선택적)
            ("localhost", 6379),  # Redis (선택적)
        ])
    
    result = await checker.check_network_connectivity(hosts=hosts)
    
    return result


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    시스템 헬스 체크
    
    - 전체 시스템 상태 확인
    - 각 서비스별 상태 확인
    """
    # TODO: 실제 헬스 체크 로직
    # - 데이터베이스 연결 확인
    # - Redis 연결 확인
    # - 외부 서비스 상태 확인
    
    services = {
        "database": "healthy",
        "redis": "healthy",
        "llm_service": "healthy",
    }
    
    # 실제 연결 확인 (간단한 예시)
    try:
        from app.db.session import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        logger.warning(f"데이터베이스 연결 확인 실패: {str(e)}")
        services["database"] = "unhealthy"
    
    status = "healthy"
    if any(s == "unhealthy" for s in services.values()):
        status = "unhealthy"
    
    logger.debug(f"헬스 체크 실행: status={status}")
    
    return HealthCheckResponse(
        status=status,
        services=services,
        timestamp=datetime.utcnow()
    )
