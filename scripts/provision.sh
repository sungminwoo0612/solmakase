#!/bin/bash
set -e

echo "========================================="
echo "Solmakase Development Server Provisioning"
echo "========================================="

# 시스템 업데이트
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# 기본 패키지 설치
echo "Installing basic packages..."
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    vim \
    htop \
    net-tools \
    nfs-common

# Python 3.10+ 설치 확인 및 설치
echo "Checking Python version..."
if ! command -v python3.10 &> /dev/null; then
    echo "Installing Python 3.10..."
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
fi

# Node.js 18.x 설치
echo "Installing Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# PostgreSQL 클라이언트 설치 (서버는 setup-services.sh에서 설치)
echo "Installing PostgreSQL client..."
sudo apt-get install -y postgresql-client

echo "Basic provisioning completed!"

