# CVFactory

<div align="center">
  <img src="static/images/logo.png" alt="CVFactory 로고" style="width:200px; height:auto;"/>
  <br>
  
  [![English](https://img.shields.io/badge/language-English-blue.svg)](README.md) [![한국어](https://img.shields.io/badge/language-한국어-red.svg)](README.ko.md)
</div>

## 📖 개요
CVFactory는 구직자를 위한 맞춤형 자기소개서 자동 생성 시스템입니다. 채용 공고와 지원자 정보를 기반으로 AI가 개인화된 자기소개서를 생성합니다. 자기소개서를 하나하나 쓸 시간이 없는 구직자들을 위해 개발했습니다.

## 🌐 라이브 데모

실제 작동하는 애플리케이션은 **[cvfactory.dev](https://cvfactory.dev)** 에서 확인하실 수 있습니다.

CVFactory의 모든 기능을 직접 체험하고 나만의 맞춤형 자기소개서를 생성해보세요!

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
- **GitHub Actions**: CI/CD 자동화
- **Render.com**: 클라우드 호스팅 플랫폼 (선택 사항)

## 🔄 환경 전환

이 프로젝트는 개발 환경과 배포 환경을 지원합니다. 제공된 스크립트를 사용하여 환경을 전환하세요:

```bash
# 개발 환경으로 전환 (기본값)
./switch_env.sh development  # Linux/macOS
.\switch_env.bat development  # Windows

# 배포 환경으로 전환
./switch_env.sh production  # Linux/macOS
.\switch_env.bat production  # Windows
```

## 🚢 GitHub Actions를 통한 CI/CD 파이프라인

CVFactory는 GitHub Actions를 사용한 CI/CD 파이프라인을 통해 자동으로 테스트, 빌드, 배포됩니다:

1. **환경 디버깅**: 환경 설정을 확인하고 보고서 생성
2. **테스트**: Django 테스트를 실행하여 코드 품질 확인
3. **빌드**: 배포를 위한 애플리케이션 준비
4. **배포**: 브랜치(develop 또는 main)에 따라 자동으로 배포

CI/CD 설정을 확인하려면 `.github/workflows/ci-cd.yml` 파일을 참조하세요.

### GitHub 브랜치 전략

개발 워크플로를 최적화하고 배포 비용을 관리하기 위해 간단하고 효과적인 브랜칭 전략을 사용합니다:

1. **`develop` 브랜치**: 모든 일상적인 개발 작업이 여기서 이루어집니다
   - 배포를 트리거하지 않고 코드를 자주 푸시할 수 있습니다
   - 테스트 및 기능 개발에 사용
   - 이 브랜치에서는 Render 파이프라인이 트리거되지 않습니다

2. **`main` 브랜치**: 프로덕션 준비가 완료된 코드만 포함
   - 배포 준비가 되었을 때만 main으로 병합
   - main에 푸시하면 자동으로 Render 배포가 트리거됨
   - 파이프라인 사용 비용을 최소화하는 데 도움이 됩니다

#### 개발 워크플로우

```bash
# develop 브랜치에서 작업 시작
git checkout develop

# 변경사항 작업 및 커밋
git add .
git commit -m "변경 내용"
git push origin develop  # 배포가 트리거되지 않음

# 배포 준비가 되었을 때
git checkout main
git merge develop
git push origin main  # Render 배포 트리거
git checkout develop  # develop 브랜치로 돌아가기
```

이 접근 방식을 통해 개발 중에는 빈번한 커밋을 하면서도 배포 시기를 제어할 수 있습니다.

### CI/CD 설정 방법

GitHub Actions로 CI/CD를 설정하려면 GitHub 저장소에 다음 Secrets을 추가하세요:

1. **배포 자격 증명**
   - `RENDER_API_KEY`: Render.com API 키
   - `RENDER_DEV_SERVICE_ID`: 개발 환경 서비스 ID
   - `RENDER_PROD_SERVICE_ID`: 프로덕션 환경 서비스 ID

2. **환경 변수**
   - `DJANGO_SECRET_KEY`: Django 보안 키
   - `ALLOWED_HOSTS`: 허용된 호스트 목록 (쉼표로 구분)
   - `GOOGLE_CLIENT_ID`: Google OAuth 클라이언트 ID
   - `GOOGLE_CLIENT_SECRET`: Google OAuth 클라이언트 시크릿
   - `GROQ_API_KEY`: Groq API 키
   - `API_KEY`: 백엔드 API 인증 키
   - `CSRF_TRUSTED_ORIGINS`: CSRF 허용 출처
   - `CORS_ALLOWED_ORIGINS`: CORS 허용 출처
   - `DOMAIN_NAME`: 커스텀 도메인 이름 (선택사항)

브랜치 관리:
- `develop` 브랜치: 개발 환경으로 자동 배포
- `main` 브랜치: 프로덕션 환경으로 자동 배포

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

## 📊 로깅 설정

CVFactory는 개발 환경과 배포 환경에 따라 로깅 설정이 다르게 적용됩니다:

### 개발 환경 로깅
- **로그 레벨**: DEBUG (모든 로그 기록)
- **콘솔 출력**: 활성화 (디버깅 용이)
- **추가 로그 파일**:
  - `debug.log`: 디버그 수준의 상세 로그
  - `groq_service_debug.log`: API 호출 관련 상세 로그
  - `logs/crawling/`: 크롤링 결과 저장 디렉토리
- **SQL 쿼리 로깅**: 활성화 (성능 최적화 용도)

### 배포 환경 로깅
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

## 🔒 보안 가이드

CVFactory를 안전하게 실행하기 위한 보안 가이드입니다:

- API 키 등의 민감한 정보는 절대로 Git에 커밋하지 마세요
- 배포 환경에서는 항상 HTTPS를 사용하세요
- 로그 파일에 민감한 정보가 기록되지 않도록 로깅 레벨을 적절히 조정하세요
- `SECURITY_GUIDELINES.md`의 권장 사항을 따르세요

### API 보안 기능

CVFactory는 API 접근을 보호하기 위한 여러 보안 조치를 구현하고 있습니다:

1. **인증 필수**: 로그인 및 회원가입과 같은 공개 엔드포인트를 제외한 모든 API 엔드포인트는 사용자 인증이 필요합니다.

2. **레퍼러 확인**: API 호출은 귀하의 웹사이트 도메인에서 시작된 요청으로 제한되어, 승인되지 않은 외부 접근을 방지합니다.

3. **요청 속도 제한**: 악용을 방지하기 위해 요청 횟수를 제한합니다:
   - IP 기반 속도 제한: 분당 최대 60개 요청
   - 사용자 기반 속도 제한: 인증된 사용자당 분당 최대 120개 요청

4. **세션 유효성 검증**: API 요청에는 유효한 세션이 필요하며, 이를 통해 웹사이트 방문자만 서비스를 이용할 수 있도록 보장합니다.

### API 인증 예시

API 엔드포인트 호출 시 인증 헤더가 필요합니다:

```javascript
// API 호출 예시
fetch('/api/generate-letter/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': 'your-api-key-here',  // API 키 헤더 추가
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify(data)
});
```

## 🚀 Render.com 배포

CVFactory는 개발 및 프로덕션 환경을 모두 제공하는 클라우드 플랫폼인 Render.com에 배포할 수 있습니다.

### 환경 설정

1. **개발 환경**
   - URL: `https://cvfactory-dev.onrender.com` (또는 사용자 지정 개발 URL)
   - 목적: 새로운 기능, 개발 코드 및 통합 테스트
   - 데이터베이스: 개발 목적의 별도 데이터베이스

2. **프로덕션 환경**
   - URL: `https://cvfactory-prod.onrender.com` (및 구성된 경우 사용자 지정 도메인)
   - 목적: 실제 사용자를 위한 라이브 서비스
   - 데이터베이스: 정기적인 백업이 있는 프로덕션 데이터베이스

### 배포 단계

1. **Render에서 웹 서비스 생성**:
   - GitHub 저장소 연결
   - Python 환경 선택
   - 빌드 명령어 설정: `./build.sh`
   - 시작 명령어 설정: `gunicorn cvfactory.asgi:application -k uvicorn.workers.UvicornWorker`

2. **환경 변수 구성**:
   - 필수 변수:
     - `ALLOWED_HOSTS`: Render 도메인 및 사용자 지정 도메인 추가
     - `CSRF_TRUSTED_ORIGINS`: 도메인의 `https://` URL 추가
     - `CORS_ALLOWED_ORIGINS`: 도메인의 `https://` URL 추가
     - `DATABASE_URL`: Render에서 자동으로 제공
     - `SECRET_KEY`: 안전한 키 생성
     - `DEBUG`: 프로덕션에서는 `False`로 설정

3. **데이터베이스 설정**:
   - Render는 자동으로 PostgreSQL 데이터베이스 제공
   - 빌드 스크립트를 통해 배포 중 마이그레이션 실행

4. **사용자 지정 도메인 구성** (프로덕션용):
   - Render 대시보드에서 웹 서비스 설정으로 이동
   - 사용자 지정 도메인 추가 (예: `cvfactory.dev`)
   - DNS 설정을 통해 도메인 소유권 확인
   - SSL 인증서 자동 발급

### 배포 모범 사례

- 프로덕션에 배포하기 전에 개발 환경에서 변경 사항 테스트
- 다양한 배포 대상에 대해 환경별 설정 사용
- Render 대시보드에서 정기적으로 로그 모니터링
- 비용 효율성을 위해 사용하지 않을 때는 개발 서비스 일시 중지 가능

## 📄 라이센스

이 프로젝트는 크리에이티브 커먼즈 저작자표시-비영리 4.0 국제 라이선스(CC BY-NC 4.0) 하에 배포됩니다. 이는 다음을 의미합니다:

- 적절한 출처를 밝히는 한 비영리 목적으로 자유롭게 공유하고 수정할 수 있습니다.
- 상업적 목적으로는 이 자료를 사용할 수 없습니다.

자세한 내용은 `LICENSE` 파일을 참조하거나 [크리에이티브 커먼즈 BY-NC 4.0](http://creativecommons.org/licenses/by-nc/4.0/) 웹사이트를 방문하세요.

## 📬 연락처

문의 사항은 다음 주소로 연락주세요:  
wintrover@gmail.com 