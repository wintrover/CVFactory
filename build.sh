#!/bin/bash
# 오류 발생 시 스크립트 종료
set -o errexit

# logs 디렉토리 생성
mkdir -p logs
mkdir -p static
mkdir -p frontend
mkdir -p staticfiles

# 필요한 패키지 설치
pip install -r requirements.txt
pip install 'whitenoise[brotli]' waitress django-extensions werkzeug pyOpenSSL

# 정적 파일 수집
python manage.py collectstatic --noinput

# 데이터베이스 마이그레이션
python manage.py migrate --noinput

echo "빌드 완료!" 