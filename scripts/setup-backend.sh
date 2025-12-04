#!/bin/bash
set -e

echo "========================================="
echo "Setting up Backend Environment"
echo "========================================="

cd /vagrant/backend

# Python 가상환경 생성
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# 가상환경 활성화
source .venv/bin/activate

# pip 업그레이드
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# 의존성 설치
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 추가 의존성 (ChromaDB 등)
echo "Installing additional dependencies..."
pip install chromadb

# 환경 변수 파일 생성 (없는 경우)
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Application
APP_NAME=Solmakase
DEBUG=True

# Database
DATABASE_URL=postgresql://solmakase:solmakase@localhost:5432/solmakase

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000

# File Upload
MAX_UPLOAD_SIZE=52428800
ALLOWED_FILE_TYPES=pdf,docx,pptx,hwp
UPLOAD_DIR=./uploads

# LLM
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4
LLM_TIMEOUT=300

# Document Retention
DOCUMENT_RETENTION_DAYS=7

# Deployment
DEPLOYMENT_TIMEOUT=1800
EOF
    echo ".env file created. Please update OPENAI_API_KEY if needed."
fi

# 업로드 디렉토리 생성
mkdir -p uploads

# 데이터베이스 마이그레이션 (PostgreSQL이 실행 중일 때)
echo "Running database migrations..."
if command -v psql &> /dev/null; then
    # PostgreSQL이 실행 중인지 확인
    if sudo systemctl is-active --quiet postgresql; then
        # 데이터베이스가 이미 생성되어 있는지 확인
        if ! psql -U solmakase -h localhost -d solmakase -c "SELECT 1" &> /dev/null; then
            echo "Database will be created by setup-services.sh"
        else
            alembic upgrade head || echo "Migration skipped (database may not be ready)"
        fi
    else
        echo "PostgreSQL is not running. Migrations will run after service setup."
    fi
fi

echo "Backend setup completed!"

