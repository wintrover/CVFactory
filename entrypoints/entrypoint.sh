#!/bin/bash
# 로그 디렉토리 확인
if [ ! -d "/app/logs" ]; then
    mkdir -p /app/logs
    echo "로그 디렉토리 생성 완료"
fi

# 정적 파일 수집
python manage.py collectstatic --no-input

# 데이터베이스 마이그레이션
python manage.py migrate

# 포트 설정
PORT="${PORT:-8000}"

# 서버 실행
echo "Starting server on 0.0.0.0:$PORT"
gunicorn --bind 0.0.0.0:$PORT cvfactory.wsgi:application 