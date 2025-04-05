# CVFactory

<div align="center">
  <img src="static/images/logo.png" alt="CVFactory 로고" style="width:200px; height:auto;"/>
  <br>
  
  [![English](https://img.shields.io/badge/language-English-blue.svg)](README.md) [![한국어](https://img.shields.io/badge/language-한국어-red.svg)](README.ko.md)
</div>

## 📖 개요
CVFactory는 구직자를 위한 맞춤형 자기소개서 자동 생성 시스템입니다. 채용 공고와 지원자 정보를 기반으로 AI가 개인화된 자기소개서를 생성합니다.

## ✨ 주요 기능

- **📄 채용 공고 크롤링**: 채용 사이트 URL을 입력하면 관련 채용 정보를 자동으로 수집
- **🏢 기업 정보 크롤링**: 기업 홈페이지 URL을 통해 기업의 비전, 미션, 가치관 등 정보 수집
- **📝 맞춤형 자기소개서 생성**: Groq API를 활용하여 개인화된 자기소개서 자동 생성

## 🚀 설치 및 실행 방법

### 로컬 개발 환경 설정

1. 레포지토리 클론:
```bash
git clone https://github.com/yourusername/CVFactory.git
cd CVFactory
```

2. 가상 환경 설정 및 패키지 설치:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 환경 변수 설정:
   - `.env.example` 파일을 복사하여 `.env`로 만들고 실제 API 키 등을 입력하세요
   - Groq API 키를 환경 변수에 설정하세요

4. 데이터베이스 마이그레이션:
```bash
python manage.py migrate
```

5. 서버 실행:
```bash
python manage.py runserver
```

6. 브라우저에서 `http://127.0.0.1:8000`으로 접속

### 도커를 사용한 실행 방법

1. 레포지토리 클론 후 도커 컨테이너 빌드 및 실행:
```bash
git clone https://github.com/yourusername/CVFactory.git
cd CVFactory
docker-compose up --build
```

2. 브라우저에서 `http://localhost:8000`으로 접속

## 📁 프로젝트 구조

```
CVFactory/
├── api/                # API 로직 및 Groq 서비스
├── crawlers/           # 채용 공고 및 기업 정보 크롤링 모듈
├── cvfactory/          # 프로젝트 설정 파일
├── data_management/    # 사용자 데이터 관리 모듈
├── frontend/           # 프론트엔드 파일
├── logs/               # 로그 파일 디렉토리
├── myapp/              # 메인 앱 모듈
├── static/             # 정적 파일
├── Dockerfile          # 도커 설정 파일
├── docker-compose.yml  # 도커 컴포즈 설정
├── manage.py           # Django 관리 스크립트
├── requirements.txt    # 의존성 패키지 목록
└── README.md           # 프로젝트 설명
```

## 🛠 기술 스택

### 백엔드
- **Django**: 웹 백엔드 프레임워크
- **Django REST Framework**: RESTful API 구현
- **Groq API**: AI 기반 자기소개서 생성
- **Selenium**: 웹 크롤링 자동화
- **BeautifulSoup**: HTML 파싱

### 프론트엔드
- **HTML/CSS/JavaScript**: 기본 UI 구현
- **Bootstrap**: 반응형 디자인

### 배포 및 개발 환경
- **Docker**: 컨테이너화 및 배포
- **Git**: 버전 관리

## 🌐 API 엔드포인트

| 엔드포인트 | 메소드 | 설명 |
|----------|--------|-------------|
| `/api/job-crawler/` | POST | URL에서 채용 공고 크롤링 |
| `/api/company-info/` | POST | 기업 정보 검색 |
| `/api/generate-letter/` | POST | 자기소개서 생성 |
| `/api/user-letters/` | GET | 사용자의 저장된 자기소개서 조회 |
| `/api/user-profile/` | GET/PUT | 사용자 프로필 조회 및 수정 |

## 🔧 환경 설정

이 프로젝트는 환경 변수를 통한 설정을 사용합니다. 다음 단계로 환경을 설정하세요:

1. 예제 환경 파일을 복사합니다:
```bash
cp .env.example .env
```

2. `.env` 파일을 편집하고 적절한 값을 설정합니다:
   - 개발 환경에서는 `DEBUG=True`, 운영 환경에서는 `DEBUG=False` 설정
   - `ALLOWED_HOSTS`에 도메인 이름 설정
   - Google OAuth 인증 정보 추가
   - Groq API 키 설정
   - 필요에 따라 보안 설정 구성

도커 환경에서는 이러한 변수들이 `.env` 파일에서 자동으로 로드됩니다.

## 환경 설정

이 프로젝트는 개발 환경과 배포 환경을 분리하여 관리합니다.

### 환경 전환하기

환경을 전환하려면 제공된 스크립트를 사용하세요:

```bash
# 개발 환경으로 전환 (기본값)
./switch_env.sh development

# 배포 환경으로 전환
./switch_env.sh production
```

### 환경 파일 설정

1. 개발 환경:
   - `.env.example` 파일을 복사하여 `.env`로 만들고 실제 API 키 등을 입력하세요.
   
2. 배포 환경:
   - 프로덕션 환경에서는 서버의 시스템 환경변수에서 민감한 정보를 가져옵니다.
   - 서버 환경에 다음 환경변수를 설정해야 합니다:
     - `SECRET_KEY`: Django 보안 키
     - `ALLOWED_HOSTS`: 허용할 호스트 목록 (쉼표로 구분)
     - `GOOGLE_CLIENT_ID`: Google OAuth 클라이언트 ID
     - `GOOGLE_CLIENT_SECRET`: Google OAuth 클라이언트 시크릿
     - `GROQ_API_KEY`: Groq API 키
     - `CSRF_TRUSTED_ORIGINS`: CSRF 허용 출처 (쉼표로 구분)
     - `CORS_ALLOWED_ORIGINS`: CORS 허용 출처 (쉼표로 구분)

### 보안 권장사항

- API 키 등의 민감한 정보는 절대로 Git에 커밋하지 마세요.
- 배포 환경에서는 항상 HTTPS를 사용하세요.
- 로그 파일에 민감한 정보가 기록되지 않도록 로깅 레벨을 적절히 조정하세요.

## 보안 가이드

CVFactory를 안전하게 실행하기 위한 보안 가이드입니다.

### API 키 인증

API 엔드포인트를 호출할 때 API 키 인증이 필요합니다:

```javascript
// API 호출 예시
fetch('/api/create_resume/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': 'your-api-key-here',  // API 키 헤더 추가
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify(data)
});
```

### 환경 변수 설정

API 키 및 보안 설정을 위한 환경 변수:

- `API_KEY`: API 호출 인증을 위한 키
- `SESSION_COOKIE_SECURE`: HTTPS 연결에서만 세션 쿠키 전송 (프로덕션: True)
- `CSRF_COOKIE_SECURE`: HTTPS 연결에서만 CSRF 쿠키 전송 (프로덕션: True)
- `CSRF_COOKIE_HTTPONLY`: JavaScript에서 CSRF 쿠키 접근 제한 (프로덕션: True)

### 로깅 및 민감 정보 처리

- 로그에는 민감한 개인정보가 기록되지 않도록 마스킹 처리됩니다
- 배포 환경에서는 로그 레벨을 INFO 이상으로 설정하세요

### 개발 환경과 배포 환경 분리

환경별 설정을 위해 다음 스크립트를 사용하세요:

```bash
# 개발 환경으로 전환
./switch_env.sh development

# 배포 환경으로 전환
./switch_env.sh production
```

### 입력 데이터 검증

모든 사용자 입력은 검증 및 정제됩니다:
- URL 입력은 형식 및 도메인 검증
- 텍스트 입력은 XSS 방지를 위한 HTML 태그 제거

### 보안 취약점 발견 시

보안 취약점을 발견한 경우 다음 주소로 연락해주세요:
- wintrover@gmail.com

## 환경별 로깅 설정

CVFactory는 개발 환경과 배포 환경에 따라 로깅 설정이 다르게 적용됩니다.

### 개발 환경 로깅

개발 환경에서는 디버깅을 위해 더 상세한 로그가 생성됩니다:

- **로그 레벨**: DEBUG (모든 로그 기록)
- **콘솔 출력**: 활성화 (디버깅 용이)
- **추가 로그 파일**:
  - `debug.log`: 디버그 수준의 상세 로그
  - `groq_service_debug.log`: API 호출 관련 상세 로그
  - `logs/crawling/`: 크롤링 결과 저장 디렉토리
- **SQL 쿼리 로깅**: 활성화 (성능 최적화 용도)

### 배포 환경 로깅

배포 환경에서는 보안과 성능을 위해 중요한 로그만 기록됩니다:

- **로그 레벨**: INFO (정보성 로그 이상만 기록)
- **콘솔 출력**: 비활성화
- **필수 로그 파일**:
  - `django.log`: 일반 애플리케이션 로그
  - `api.log`: API 호출 관련 로그
  - `error.log`: 오류 수준 로그
  - `security.log`: 보안 관련 로그
- **SQL 쿼리 로깅**: 비활성화

### 로그 설정 변경 방법

환경 변수를 통해 로깅 설정을 조정할 수 있습니다:

```bash
# 개발 환경에서 더 자세한 로그 활성화
LOG_LEVEL=DEBUG
LOG_TO_CONSOLE=True
LOG_SQL_QUERIES=True

# 배포 환경에서 중요 로그만 기록
LOG_LEVEL=INFO
LOG_TO_CONSOLE=False
LOG_SQL_QUERIES=False
```

## CI/CD 배포 자동화

CVFactory는 GitHub Actions를 사용한 CI/CD 파이프라인을 통해 자동으로 테스트, 빌드, 배포됩니다.

### CI/CD 설정 방법

1. GitHub 저장소에 다음 Secrets을 추가하세요:

   **공통 설정**
   - `AWS_ACCESS_KEY_ID`: AWS 접근 키
   - `AWS_SECRET_ACCESS_KEY`: AWS 비밀 키

   **배포 환경 변수**
   - `DJANGO_SECRET_KEY`: Django 보안 키
   - `ALLOWED_HOSTS`: 허용된 호스트 목록 (쉼표로 구분)
   - `GOOGLE_CLIENT_ID`: Google OAuth 클라이언트 ID
   - `GOOGLE_CLIENT_SECRET`: Google OAuth 클라이언트 시크릿
   - `GROQ_API_KEY`: Groq API 키
   - `API_KEY`: 백엔드 API 인증 키
   - `CSRF_TRUSTED_ORIGINS`: CSRF 허용 출처
   - `CORS_ALLOWED_ORIGINS`: CORS 허용 출처
   - `DOMAIN_NAME`: 커스텀 도메인 이름 (선택사항)

2. GitHub 브랜치 관리:
   - `develop` 브랜치: 개발 환경으로 자동 배포
   - `main` 브랜치: 프로덕션 환경으로 자동 배포

### GitHub Actions 워크플로우

워크플로우는 다음 단계로 구성됩니다:

1. **테스트**: 코드 품질과 기능 테스트
2. **빌드**: 환경 설정 및 정적 파일 수집
3. **배포-개발**: develop 브랜치 코드를 개발 환경에 배포
4. **배포-프로덕션**: main 브랜치 코드를 프로덕션 환경에 배포

### 수동 배포 방법

서버리스 프레임워크를 사용한 수동 배포:

```bash
# 필요한 패키지 설치
npm install

# 개발 환경 배포
npm run deploy:dev

# 프로덕션 환경 배포
npm run deploy:prod

# 로그 확인 (개발 환경)
npm run logs:dev
```

### 파일 권한 문제 해결

배포 과정에서 파일 권한 문제가 발생할 경우:

```bash
# 로그 디렉토리 권한 설정
chmod -R 755 logs/

# 정적 파일 디렉토리 권한 설정
chmod -R 755 staticfiles/
```

## 📄 라이센스

이 프로젝트는 크리에이티브 커먼즈 저작자표시-비영리 4.0 국제 라이선스(CC BY-NC 4.0) 하에 배포됩니다. 이는 다음을 의미합니다:

- 적절한 출처를 밝히는 한 비영리 목적으로 자유롭게 공유하고 수정할 수 있습니다.
- 상업적 목적으로는 이 자료를 사용할 수 없습니다.

자세한 내용은 `LICENSE` 파일을 참조하거나 [크리에이티브 커먼즈 BY-NC 4.0](http://creativecommons.org/licenses/by-nc/4.0/) 웹사이트를 방문하세요.

## 📬 연락처

문의 사항은 다음 주소로 연락주세요:  
wintrover@gmail.com 