#!/bin/bash
# 로그 디렉토리 확인
if [ ! -d "/app/logs" ]; then
    mkdir -p /app/logs
    echo "로그 디렉토리 생성 완료"
fi

# 데이터베이스 마이그레이션
echo "데이터베이스 마이그레이션 실행..."
python manage.py migrate --noinput

# 정적 파일 수집
echo "정적 파일 수집 중..."
python manage.py collectstatic --noinput

# 서버 실행 (plain HTTP 사용)
echo "서버 시작... (HTTP)"
exec python manage.py runserver 0.0.0.0:8000 