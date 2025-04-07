#!/bin/bash

set -o errexit  # 오류 발생 시 스크립트 종료
set -o nounset  # 정의되지 않은 변수 사용 시 오류 발생

echo "프로덕션 환경 진입점 스크립트 시작"

# 환경 변수 확인
echo "실행 환경: $ENVIRONMENT"
echo "Django 디버그 모드: $DEBUG"
echo "허용 호스트: $ALLOWED_HOSTS"

# DATABASE_URL 환경 변수가 설정되어 있는지 확인
if [ -z "${DATABASE_URL:-}" ]; then
    echo "경고: DATABASE_URL 환경 변수가 설정되지 않았습니다. 데이터베이스 연결 확인을 건너뜁니다."
    DATABASE_AVAILABLE=false
else
    # 데이터베이스 연결 대기
    echo "데이터베이스 연결 확인 중..."
    python << END
import sys
import time
import psycopg2
from urllib.parse import urlparse

# DATABASE_URL 파싱
url = urlparse("$DATABASE_URL")
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port or 5432

# 연결 시도
retry_count = 0
max_retries = 10
retry_interval = 3  # 초

while retry_count < max_retries:
    try:
        print(f"데이터베이스 연결 시도 중... (시도 {retry_count + 1}/{max_retries})")
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.close()
        print("데이터베이스 연결 성공!")
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f"데이터베이스 연결 실패: {e}")
        retry_count += 1
        if retry_count < max_retries:
            print(f"{retry_interval}초 후 재시도합니다...")
            time.sleep(retry_interval)
        else:
            print("최대 재시도 횟수 초과. 데이터베이스에 연결할 수 없습니다.")
            sys.exit(1)
END
    DATABASE_AVAILABLE=true
fi

# 마이그레이션 실행
if [ "${DATABASE_AVAILABLE:-false}" = "true" ]; then
    echo "데이터베이스 마이그레이션 실행 중..."
    python manage.py migrate --no-input || echo "마이그레이션 실패, 계속 진행합니다."
else
    echo "경고: 데이터베이스 연결을 사용할 수 없어 마이그레이션을 건너뜁니다."
fi

# 정적 파일 수집
echo "정적 파일 수집 중..."
python manage.py collectstatic --no-input --noinput || echo "정적 파일 수집 실패, 계속 진행합니다."

# Gunicorn으로 서버 시작
echo "Gunicorn으로 서버 시작 중..."
gunicorn cvfactory.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 