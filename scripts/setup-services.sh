#!/bin/bash
set -e

echo "========================================="
echo "Setting up System Services"
echo "========================================="

# PostgreSQL 설치 및 설정
if ! command -v psql &> /dev/null || ! sudo systemctl is-active --quiet postgresql; then
    echo "Installing PostgreSQL..."
    sudo apt-get install -y postgresql postgresql-contrib
    
    # PostgreSQL 서비스 시작
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # 데이터베이스 및 사용자 생성
    echo "Setting up PostgreSQL database..."
    sudo -u postgres psql << EOF
-- Create user
CREATE USER solmakase WITH PASSWORD 'solmakase';

-- Create database
CREATE DATABASE solmakase OWNER solmakase;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE solmakase TO solmakase;

-- Allow connections
ALTER USER solmakase CREATEDB;
EOF

    # PostgreSQL 설정 수정 (로컬 연결 허용)
    sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/*/main/postgresql.conf
    sudo sed -i "s/host    all             all             127.0.0.1\/32            scram-sha-256/host    all             all             127.0.0.1\/32            md5/" /etc/postgresql/*/main/pg_hba.conf
    sudo sed -i "$ a host    all             all             0.0.0.0\/0               md5" /etc/postgresql/*/main/pg_hba.conf
    
    # PostgreSQL 재시작
    sudo systemctl restart postgresql
    echo "PostgreSQL installed and configured."
else
    echo "PostgreSQL is already installed and running."
fi

# Redis 설치 및 설정
if ! command -v redis-server &> /dev/null || ! sudo systemctl is-active --quiet redis-server; then
    echo "Installing Redis..."
    sudo apt-get install -y redis-server
    
    # Redis 설정 수정
    sudo sed -i "s/bind 127.0.0.1 ::1/bind 0.0.0.0/" /etc/redis/redis.conf
    sudo sed -i "s/protected-mode yes/protected-mode no/" /etc/redis/redis.conf
    
    # Redis 서비스 시작
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    echo "Redis installed and configured."
else
    echo "Redis is already installed and running."
fi

# Terraform 설치
if ! command -v terraform &> /dev/null; then
    echo "Installing Terraform..."
    TERRAFORM_VERSION="1.6.0"
    wget -q https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip
    unzip -q terraform_${TERRAFORM_VERSION}_linux_amd64.zip
    sudo mv terraform /usr/local/bin/
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip
    echo "Terraform installed."
else
    echo "Terraform is already installed."
fi

# 시스템 서비스 상태 확인
echo ""
echo "Service Status:"
echo "==============="
sudo systemctl status postgresql --no-pager -l | head -3
sudo systemctl status redis-server --no-pager -l | head -3

echo ""
echo "Services setup completed!"

