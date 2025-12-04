#!/bin/bash
set -e

echo "========================================="
echo "Setting up Frontend Environment"
echo "========================================="

cd /vagrant/front

# Node.js 버전 확인
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

# 의존성 설치
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
else
    echo "Updating npm dependencies..."
    npm install
fi

# 환경 변수 파일 생성 (없는 경우)
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF
    echo ".env file created."
fi

echo "Frontend setup completed!"

