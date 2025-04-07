#!/usr/bin/env pwsh
# Render 환경 시뮬레이션을 위한 PowerShell 스크립트

# 환경변수 설정
$env:DEBUG = "False"
$env:RENDER = "true"
$env:RENDER_EXTERNAL_HOSTNAME = "localhost"
$env:DATABASE_URL = "sqlite:///db.sqlite3"
$env:DJANGO_SECRET_KEY = "local-test-key-for-render-simulation"
$env:ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:CSRF_TRUSTED_ORIGINS = "http://localhost:8000,http://127.0.0.1:8000"
$env:CORS_ALLOWED_ORIGINS = "http://localhost:8000,http://127.0.0.1:8000"

Write-Host "==> Render 환경 변수 설정 완료" -ForegroundColor Blue

# conda 환경 활성화 (이미 활성화되어 있다면 생략 가능)
Write-Host "==> conda 환경 활성화" -ForegroundColor Blue
conda activate cvfactory

# 필요한 디렉토리 생성
Write-Host "==> 필요한 디렉토리 생성" -ForegroundColor Blue
mkdir -Force logs
mkdir -Force static
mkdir -Force frontend
mkdir -Force staticfiles

# 필요한 패키지 설치 확인
Write-Host "==> 필요한 패키지 설치 확인" -ForegroundColor Blue
pip install -r requirements.txt
pip install 'whitenoise[brotli]'

# 정적 파일 수집
Write-Host "==> 정적 파일 수집" -ForegroundColor Blue
python manage.py collectstatic --no-input

# 데이터베이스 마이그레이션
Write-Host "==> 데이터베이스 마이그레이션" -ForegroundColor Blue
python manage.py migrate

# Gunicorn으로 서버 실행 (Windows에서는 waitress 사용)
Write-Host "==> 서버 실행 (Ctrl+C로 중지)" -ForegroundColor Green
pip install waitress
waitress-serve --port=8000 cvfactory.wsgi:application 