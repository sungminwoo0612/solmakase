#!/bin/bash
set -e

echo "========================================="
echo "Starting Solmakase Services"
echo "========================================="

# 백엔드 서비스 시작
echo "Starting backend service..."
cd /vagrant/backend
source .venv/bin/activate

# 데이터베이스 마이그레이션
echo "Running database migrations..."
alembic upgrade head

# 백그라운드에서 FastAPI 서버 시작
echo "Starting FastAPI server on port 8000..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/fastapi.log 2>&1 &
echo $! > /tmp/fastapi.pid
echo "FastAPI server started (PID: $(cat /tmp/fastapi.pid))"

# 프론트엔드 서비스 시작
echo "Starting frontend service..."
cd /vagrant/front
nohup npm run dev -- --host 0.0.0.0 > /tmp/vite.log 2>&1 &
echo $! > /tmp/vite.pid
echo "Vite dev server started (PID: $(cat /tmp/vite.pid))"

echo ""
echo "Services started!"
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"

