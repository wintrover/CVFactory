# CVFactory - AI 자기소개서 생성기

<div align="center">
  <img src="logo.png" alt="CVFactory Logo" style="width:200px; height:auto;"/>
  <br>

  [![English](https://img.shields.io/badge/language-English-blue.svg)](README.md)
</div>

## 📖 개요
CVFactory는 사용자가 채용 공고와 자신의 스토리를 입력하여 맞춤형 자기소개서를 쉽게 생성할 수 있도록 돕는 AI 기반 웹 애플리케이션입니다.

## ✨ 주요 기능
- 채용 공고 URL 및 회사 공식 URL 기반 정보 추출
- 사용자 스토리 입력 및 분석
- 입력 정보를 활용한 AI 기반 자기소개서 초안 생성
- 생성된 자기소개서 확인 및 수정 기능

## 🛠 기술 스택
| 분류 | 기술 요소 |
|----------|--------------|
| 프레임워크 | Django |
| 프론트엔드 | HTML, CSS, JavaScript |
| AI/ML | Gemini 2.5 Flash API |
| 데이터베이스 | SQLite (개발), PostgreSQL (dj-database-url을 통한 프로덕션) |
| 웹 서버 | Gunicorn |
| 정적 파일 | Whitenoise |
| HTTP 클라이언트 | Requests |
| 환경 변수 | python-dotenv |
| 배포 | Northflank, Docker, Docker Compose, Cloudflare (캐싱용) |

## 🚀 시작하기

### 필수 요구사항
- Python 3.8+
- uv (Python 패키지 설치 및 관리 도구)
- Git
- Docker (선택 사항, 컨테이너화된 배포 시 필요)
- Conda (가상 환경 관리를 위해 권장)

### 설치 및 실행

1. **리포지토리 클론:**
   ```bash
   git clone https://github.com/wintrover/CVFactory.git
   cd CVFactory
   ```

2. **Conda 환경 설정 및 활성화:**
   ```bash
   conda create -n cvfactory python=3.8
   conda activate cvfactory
   ```

3. **uv 설치 (설치되어 있지 않다면):**
   ```bash
   # uv 설치 방법은 공식 문서를 참고하십시오:
   # https://github.com/astral-sh/uv#installation
   # pipx를 사용한 예시:
   # pipx install uv
   ```

4. **uv를 사용하여 종속성 설치:**
   ```bash
   uv pip install -r requirements.txt  # requirements.txt 파일이 있다면 실행
   # 또는 필요한 라이브러리를 개별 설치 (예: uv pip install django)
   ```

5. **데이터베이스 마이그레이션 (Django 사용 시):**
   ```bash
   python manage.py migrate
   ```

6. **개발 서버 실행:**
   ```bash
   python manage.py runserver
   ```

   브라우저에서 `http://127.0.0.1:8000/` (또는 설정된 포트)로 접속하여 애플리케이션을 확인합니다.

### Docker를 사용한 빌드 및 실행 (선택 사항)

프로젝트에 Dockerfile이 있다면 다음 명령어로 빌드 및 실행이 가능합니다.

```bash
# Docker 이미지 빌드
docker build -t cvfactory .

# Docker 컨테이너 실행
docker run -p 8000:8000 cvfactory
```

## 🐳 Northflank 배포
Northflank를 사용하여 이 프로젝트를 배포할 수 있습니다. Northflank 설정 및 배포 방법에 대한 자세한 내용은 Northflank 문서를 참고하십시오.

## 📁 프로젝트 구조
```
CVFactory/
├── manage.py              # Django 관리 스크립트
├── requirements.txt       # Python 종속성
├── Dockerfile             # Docker 이미지 정의
├── docker-compose.yml     # Docker Compose를 사용한 로컬 개발/테스트
├── northflank.json        # Northflank 배포 설정
├── purge_cloudflare_cache.py # Cloudflare 캐시 퍼지 스크립트
├── LICENSE                # 프로젝트 라이선스 (CC BY NC 4.0)
├── README.md              # 영어 README
├── README.kr.md           # 한국어 README
├── index.html             # 메인 HTML 파일
├── style.css              # 메인 CSS 파일
├── script.js              # 메인 JavaScript 파일
├── db.sqlite3             # 기본 SQLite 데이터베이스 파일 (개발)
├── config/                # Django 프로젝트 설정, URL, WSGI/ASGI
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── __init__.py
└── core/                  # Django 코어 애플리케이션 (뷰)
    ├── views.py
    └── __init__.py
```