# CVFactory 환경 관리 가이드

CVFactory는 개발 환경과 프로덕션 환경을 쉽게 전환할 수 있도록 설계되었습니다. 
이 가이드는 환경 설정 방법과 도커 환경에서의 실행 방법을 설명합니다.

## 환경 설정

### 개발 환경과 프로덕션 환경

두 개의 환경 설정 파일이 있습니다:
- `.env.development`: 개발 환경 설정
- `.env.production`: 프로덕션 환경 설정

사용할 환경에 맞게 `.env` 파일을 복사해서 사용하세요:

```bash
# 개발 환경 사용 시
cp .env.development .env

# 프로덕션 환경 사용 시
cp .env.production .env
```

### VS Code에서 실행

VS Code에서는 태스크를 사용하여 환경을 전환할 수 있습니다:

1. `Ctrl+Shift+P` (또는 `Cmd+Shift+P`)를 누르고 `Tasks: Run Task` 선택
2. 다음 중 하나의 태스크 선택:
   - `Docker: 개발 환경 실행`
   - `Docker: 프로덕션 환경 실행`

## Docker 환경에서 실행하기

### 개발 환경에서 실행

```bash
# 개발 환경 설정 사용
cp .env.development .env

# 도커 컴포즈로 실행
docker-compose -f docker-compose.dev.yml up
```

또는 VS Code 태스크:
- `Docker: 개발 환경 실행`

### 개발 환경에서 Watch 모드로 실행 (코드 변경 자동 감지)

```bash
# 개발 환경에서 Docker Compose Watch 실행
docker compose -f docker-compose.dev.yml watch
```

또는 VS Code 태스크:
- `Docker: 개발 환경 실행 (Watch 모드)`

Watch 모드는 코드 변경을 실시간으로 감지하여 컨테이너에 동기화합니다.
주요 디렉토리(cvfactory, api, myapp, data_management, frontend)의 
변경사항이 자동으로 컨테이너에 반영됩니다.

### 프로덕션 환경에서 실행 (로컬 테스트용)

```bash
# 프로덕션 환경 설정 사용
cp .env.production .env

# 도커 컴포즈로 실행
docker-compose -f docker-compose.prod.yml up
```

또는 VS Code 태스크:
- `Docker: 프로덕션 환경 실행`

## 환경 파일 구성

### .env.development (개발 환경)

개발 환경 설정을 포함합니다:
- DEBUG=True
- 로컬 호스트 접근 설정
- 개발 모드 로그 레벨

### .env.production (프로덕션 환경)

프로덕션 환경 설정을 포함합니다:
- DEBUG=False
- 실제 도메인 설정
- CSRF/CORS 보안 설정
- Render 설정

## Docker 파일 구조

- `Dockerfile.dev`: 개발 환경용 Dockerfile
- `Dockerfile.prod`: 프로덕션 환경용 Dockerfile
- `docker-compose.dev.yml`: 개발 환경용 Docker Compose 설정
- `docker-compose.prod.yml`: 프로덕션 환경용 Docker Compose 설정

## Render에 배포하기

Render에 배포할 때는 `render.yaml` 파일이 사용됩니다. 
이 파일은 모든 필요한 환경 변수를 포함하고 있으므로, 별도의 환경 파일 수정 없이 배포할 수 있습니다.

```bash
# GitHub에 변경사항 푸시
git add .
git commit -m "배포 준비"
git push

# Render 대시보드에서 배포 시작
# https://dashboard.render.com에서 새 웹 서비스 생성
```

## 주의사항

1. 환경을 전환할 때는 해당하는 `.env` 파일을 복사해서 사용하세요.
2. 개발환경에서는 코드 변경이 자동으로 반영됩니다 (볼륨 마운트 또는 Compose Watch).
3. 프로덕션 환경에서는 변경사항을 반영하려면 컨테이너를 재시작해야 합니다.
4. Render 배포 시 데이터베이스 연결 문자열(DATABASE_URL)은 자동으로 설정됩니다. 