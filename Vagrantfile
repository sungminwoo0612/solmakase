# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Ubuntu 22.04 LTS 박스 사용
  config.vm.box = "ubuntu/jammy64"

  # VirtualBox 프로바이더 설정 (온프레미스 개발 환경)
  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.memory = 4096  # 4GB RAM
    vb.cpus = 2       # 2 CPU 코어
    vb.name = "Solmakase-Dev-Server"
  end

  # 포트 포워딩
  config.vm.network "forwarded_port", guest: 8000, host: 8000, auto_correct: true  # FastAPI
  config.vm.network "forwarded_port", guest: 5173, host: 5173, auto_correct: true  # Vite Dev Server
  config.vm.network "forwarded_port", guest: 5432, host: 5432, auto_correct: true  # PostgreSQL
  config.vm.network "forwarded_port", guest: 6379, host: 6379, auto_correct: true  # Redis
  config.vm.network "forwarded_port", guest: 3000, host: 3000, auto_correct: true  # React (alternative)

  # 호스트 이름 설정
  config.vm.hostname = "solmakase-dev"

  # 프로비저닝 스크립트 실행
  config.vm.provision "shell", path: "scripts/provision.sh", privileged: false
  config.vm.provision "shell", path: "scripts/setup-backend.sh", privileged: false
  config.vm.provision "shell", path: "scripts/setup-frontend.sh", privileged: false
  config.vm.provision "shell", path: "scripts/setup-services.sh", privileged: true

  # 프로젝트 디렉토리 동기화 (기본 VirtualBox 공유 폴더 사용)
  config.vm.synced_folder ".", "/vagrant"

  # SSH 설정
  config.ssh.insert_key = false
  config.ssh.forward_agent = true
end

