# Python 버전은 프로젝트에 맞게 조정하세요.
FROM python:3.10-slim

# 작업 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 시스템 패키지 업데이트 및 필요한 도구 설치 (필요시)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     # 예: PostgreSQL 클라이언트 (psycopg2 사용 시)
#     libpq-dev \
#     # 기타 필요한 패키지
#  && apt-get clean \
#  && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 생성 및 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 전체 복사
COPY . /app/

# 정적 파일 수집
# 이 명령어는 settings.py의 STATIC_ROOT 설정을 사용합니다.
# DEBUG=False 환경에서 정적 파일을 올바르게 서빙하기 위해 필요합니다.
# Northflank에서 빌드 시 환경변수를 설정할 수 있다면, 여기서 DEBUG=0 같은 값을 설정할 수 있습니다.
# RUN SECRET_KEY=dummy DJANGO_SETTINGS_MODULE=cvfactory_project.settings DEBUG=0 python manage.py collectstatic --noinput
RUN python manage.py collectstatic --noinput

# Northflank는 보통 8080 포트를 사용하지만, 필요시 변경 가능
# EXPOSE 8080

# Gunicorn을 사용하여 Uvicorn 워커로 ASGI 애플리케이션 실행
# CMD ["gunicorn", "cvfactory_project.asgi:application", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
# Northflank에서 Procfile 또는 직접 명령을 통해 실행하는 경우 CMD는 생략 가능
# 만약 Northflank가 PORT 환경변수를 제공한다면 아래와 같이 사용:
# CMD ["gunicorn", "cvfactory_project.asgi:application", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT"]

# 기본 CMD (포트는 Northflank 설정에 따름, 여기서는 8000으로 가정)
# Northflank가 PORT 환경변수를 주입한다면 Gunicorn의 --bind 옵션에서 $PORT를 사용하세요.
CMD gunicorn cvfactory_project.asgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --worker-class uvicorn.workers.UvicornWorker 