# Backend - Clean Architecture

FastAPI 기반 클린 아키텍처 구조

## 빠른 시작

```bash
# backend/ 디렉토리로 이동
cd backend

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (선택사항)
# .env 파일이 없으면 기본값 사용

# 서버 실행
# 방법 1: backend/ 디렉토리에서
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 방법 2: 프로젝트 루트에서
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 방법 3: Python으로 직접 실행
python main.py
```

## 디렉터리 구조

```
backend/
├── app/
│   ├── __init__.py
│   │
│   ├── api/                    # Interface Adapter Layer (API)
│   │   ├── __init__.py
│   │   ├── deps.py            # API 의존성 (인증, DB 세션 등)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── requirements.py # 요구사항 수집 API
│   │       ├── analysis.py     # 분석 결과 API
│   │       ├── infrastructure.py # 인프라 설계 API
│   │       ├── deployment.py   # 배포 관리 API
│   │       └── monitoring.py   # 모니터링 API
│   │
│   ├── core/                   # Framework Layer (설정)
│   │   ├── __init__.py
│   │   ├── config.py          # 환경 설정
│   │   ├── security.py        # 보안 (인증, 암호화)
│   │   └── dependencies.py    # FastAPI 의존성 주입
│   │
│   ├── domain/                 # Domain Layer (엔티티)
│   │   ├── __init__.py
│   │   ├── entities/          # 도메인 엔티티
│   │   │   ├── __init__.py
│   │   │   ├── requirement.py
│   │   │   ├── infrastructure.py
│   │   │   ├── deployment.py
│   │   │   └── resource.py
│   │   └── value_objects/     # 값 객체
│   │       ├── __init__.py
│   │       ├── cost.py
│   │       └── status.py
│   │
│   ├── schemas/                # Interface Adapter Layer (DTO)
│   │   ├── __init__.py
│   │   ├── requirement.py     # 요구사항 스키마
│   │   ├── infrastructure.py  # 인프라 설계 스키마
│   │   ├── deployment.py      # 배포 스키마
│   │   ├── monitoring.py      # 모니터링 스키마
│   │   └── common.py          # 공통 스키마
│   │
│   ├── services/               # Use Case Layer (비즈니스 로직)
│   │   ├── __init__.py
│   │   ├── requirement_service.py    # 요구사항 수집 및 관리
│   │   ├── file_service.py           # 파일 업로드 및 파싱
│   │   ├── llm_service.py            # LLM/RAG 연동
│   │   ├── infrastructure_service.py # 인프라 설계
│   │   ├── iac_service.py            # IaC 코드 생성
│   │   ├── deployment_service.py     # 배포 관리
│   │   └── monitoring_service.py     # 모니터링
│   │
│   ├── repositories/           # Interface Adapter Layer (데이터 접근)
│   │   ├── __init__.py
│   │   ├── interfaces/        # 리포지토리 인터페이스
│   │   │   ├── __init__.py
│   │   │   ├── requirement_repository.py
│   │   │   ├── infrastructure_repository.py
│   │   │   ├── deployment_repository.py
│   │   │   └── monitoring_repository.py
│   │   └── implementations/   # 리포지토리 구현체
│   │       ├── __init__.py
│   │       ├── requirement_repository.py
│   │       ├── infrastructure_repository.py
│   │       ├── deployment_repository.py
│   │       └── monitoring_repository.py
│   │
│   ├── models/                 # Interface Adapter Layer (ORM 모델)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── requirement.py
│   │   ├── document.py
│   │   ├── infrastructure.py
│   │   ├── iac_code.py
│   │   ├── deployment.py
│   │   ├── resource.py
│   │   └── monitoring.py
│   │
│   ├── db/                     # Framework Layer (데이터베이스)
│   │   ├── __init__.py
│   │   ├── base.py            # Base 클래스
│   │   ├── session.py         # DB 세션 관리
│   │   └── migrations/        # Alembic 마이그레이션
│   │
│   └── utils/                  # 유틸리티
│       ├── __init__.py
│       ├── file_parser.py     # 문서 파싱 (PDF, docx 등)
│       ├── validators.py      # 데이터 검증
│       └── exceptions.py      # 커스텀 예외
│
├── tests/                      # 테스트
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── alembic.ini                 # Alembic 설정
├── requirements.txt            # Python 의존성
├── .env.example               # 환경 변수 예제
└── main.py                    # FastAPI 애플리케이션 진입점
```

## 레이어 설명

### 1. Domain Layer (`domain/`)
- **역할**: 핵심 비즈니스 로직과 엔티티
- **의존성**: 외부 의존성 없음 (순수 Python)
- **구성**:
  - `entities/`: 도메인 엔티티 (Requirement, Infrastructure, Deployment 등)
  - `value_objects/`: 값 객체 (Cost, Status 등)

### 2. Use Case Layer (`services/`)
- **역할**: 비즈니스 로직 구현
- **의존성**: Domain Layer, Repository 인터페이스
- **구성**:
  - 각 도메인별 서비스 (requirement_service, infrastructure_service 등)
  - Repository 인터페이스를 통한 데이터 접근

### 3. Interface Adapter Layer
- **API** (`api/`): FastAPI 라우터 및 엔드포인트
- **Schemas** (`schemas/`): Pydantic 모델 (요청/응답 DTO)
- **Repositories** (`repositories/`): 데이터 접근 추상화
- **Models** (`models/`): SQLAlchemy ORM 모델

### 4. Framework Layer
- **Core** (`core/`): 설정, 보안, 의존성 주입
- **DB** (`db/`): 데이터베이스 연결 및 세션 관리

## 의존성 방향

```
API (api/) 
  ↓
Services (services/)
  ↓
Repositories (repositories/interfaces/)
  ↓
Models (models/) → DB (db/)
  ↓
Domain (domain/)
```

## 주요 원칙

1. **의존성 역전**: 상위 레이어가 하위 레이어의 인터페이스에 의존
2. **단일 책임**: 각 모듈은 하나의 책임만 가짐
3. **인터페이스 분리**: Repository 인터페이스로 데이터 접근 추상화
4. **의존성 주입**: FastAPI의 Depends를 통한 의존성 주입
