# Vagrant를 사용한 Solmakase 개발 환경 설정

VirtualBox에서 Vagrant를 사용하여 Solmakase 개발 서버를 프로비저닝하는 방법입니다.

## 사전 요구사항

1. **VirtualBox** 설치
2. **Vagrant** 설치

### 설치 방법

#### 1. Vagrant 설치
```bash
# Windows
# https://www.vagrantup.com/downloads 에서 다운로드

# Linux
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vagrant
```

## 사용 방법

### 1. VM 생성 및 프로비저닝
```bash
# 프로젝트 루트 디렉토리에서 실행
cd /path/to/solmakase

# VM 생성 및 프로비저닝 시작 (기본 프로바이더: virtualbox)
vagrant up
```

### 2. VM 접속
```bash
# SSH로 VM 접속
vagrant ssh

# VM 내부에서 프로젝트 디렉토리는 /vagrant에 마운트됨
cd /vagrant
```

### 3. 서비스 시작
```bash
# VM 내부에서 실행
/vagrant/scripts/start-services.sh

# 또는 수동으로 시작
# Backend
cd /vagrant/backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd /vagrant/front
npm run dev -- --host 0.0.0.0
```

### 4. 서비스 접속
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

### 5. VM 관리
```bash
# VM 중지
vagrant halt

# VM 재시작
vagrant reload

# VM 삭제
vagrant destroy

# VM 상태 확인
vagrant status

# VM 일시 중지
vagrant suspend

# VM 재개
vagrant resume
```

## 프로비저닝 스크립트

프로비저닝은 다음 순서로 실행됩니다:

1. **provision.sh**: 기본 시스템 패키지 및 도구 설치
   - Python 3.10+
   - Node.js 18.x
   - 기본 개발 도구

2. **setup-backend.sh**: 백엔드 환경 설정
   - Python 가상환경 생성
   - 의존성 설치
   - 환경 변수 파일 생성

3. **setup-frontend.sh**: 프론트엔드 환경 설정
   - npm 의존성 설치
   - 환경 변수 파일 생성

4. **setup-services.sh**: 시스템 서비스 설정
   - PostgreSQL 설치 및 설정
   - Redis 설치 및 설정
   - Terraform 설치

## 포트 포워딩

다음 포트가 호스트로 포워딩됩니다:

- `8000`: FastAPI 백엔드
- `5173`: Vite 개발 서버
- `5432`: PostgreSQL
- `6379`: Redis
- `3000`: React (대체 포트)

## 데이터베이스 접속 정보

- **호스트**: localhost
- **포트**: 5432
- **데이터베이스**: solmakase
- **사용자**: solmakase
- **비밀번호**: solmakase

## 문제 해결

### 1. VMware 플러그인 오류
```bash
# 플러그인 재설치
vagrant plugin uninstall vagrant-vmware-desktop
vagrant plugin install vagrant-vmware-desktop
```

### 2. 포트 충돌
포트가 이미 사용 중인 경우 Vagrantfile에서 포트를 변경하거나 `auto_correct: true` 옵션이 자동으로 다른 포트를 할당합니다.

### 3. 프로비저닝 실패
```bash
# 프로비저닝만 다시 실행
vagrant provision

# 특정 스크립트만 실행
vagrant provision --provision-with shell
```

### 4. NFS 동기화 문제 (Linux)
```bash
# NFS 서버 설치 (호스트)
sudo apt-get install nfs-kernel-server

# Vagrantfile에서 NFS 타입 제거 또는 'rsync' 사용
```

## 추가 설정

### 환경 변수 수정
VM 내부에서 환경 변수를 수정하려면:

```bash
# Backend
vim /vagrant/backend/.env

# Frontend
vim /vagrant/front/.env
```

### 데이터베이스 마이그레이션
```bash
cd /vagrant/backend
source .venv/bin/activate
alembic upgrade head
```

### 로그 확인
```bash
# FastAPI 로그
tail -f /tmp/fastapi.log

# Vite 로그
tail -f /tmp/vite.log
```

## 참고사항

- VM은 `/vagrant` 디렉토리에 프로젝트를 마운트합니다
- 호스트에서 파일을 수정하면 VM에서도 즉시 반영됩니다
- VM 리소스는 Vagrantfile에서 조정할 수 있습니다 (메모리, CPU)
- 프로덕션 환경에서는 이 설정을 사용하지 마세요

