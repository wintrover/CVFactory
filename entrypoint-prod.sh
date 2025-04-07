#!/bin/bash

set -o errexit  # 오류 발생 시 스크립트 종료
set -o nounset  # 정의되지 않은 변수 사용 시 오류 발생

echo "프로덕션 환경 진입점 스크립트 시작"

# 환경 변수 확인
echo "실행 환경: $ENVIRONMENT"
echo "Django 디버그 모드: $DEBUG"
echo "허용 호스트: $ALLOWED_HOSTS"

# 마이그레이션 실행
echo "데이터베이스 마이그레이션 실행 중..."
python manage.py migrate --no-input

# 정적 파일 수집
echo "정적 파일 수집 중..."
python manage.py collectstatic --no-input

# Gunicorn으로 서버 시작
echo "Gunicorn으로 서버 시작 중..."
gunicorn cvfactory.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 