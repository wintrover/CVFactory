# Python 버전은 프로젝트에 맞게 조정하세요.
FROM python:3.10-alpine

# Python Gunicorn Uvicorn Poetry 설치
RUN pip install --upgrade pip

# 작업 디렉토리 설정
WORKDIR /app

# PYTHONPATH 환경 변수 설정
ENV PYTHONPATH /app

# 환경 변수 설정 (Gunicorn 및 Uvicorn 설정)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 시스템 패키지 업데이트 및 필요한 도구 설치 (필요시)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     # 예: PostgreSQL 클라이언트 (psycopg2 사용 시)
#     libpq-dev \
#     # 기타 필요한 패키지
#  && apt-get clean \
#  && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 전체 복사
COPY . .

# 정적 파일 수집 (개발 중에는 필요 없을 수 있지만, 프로덕션 빌드에는 포함)
# RUN python manage.py collectstatic --noinput

# 포트 노출 (Northflank가 자동으로 처리할 수 있음)
# EXPOSE 8000

# 애플리케이션 실행 (ASGI 사용)
CMD ["sh", "-c", "python manage.py collectstatic --noinput ; python manage.py makemigrations ; python manage.py migrate ; gunicorn cvfactory_project.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}"] 