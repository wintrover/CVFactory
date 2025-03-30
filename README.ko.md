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
- **📊 로깅 시스템**: 서버 요청 및 응답, API 호출, 오류 등을 로그 파일에 기록

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
   - `secretkey.env` 파일을 생성하고 Django 보안 키 설정
   - `groq.env` 파일에 Groq API 키 설정

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

## 📊 로깅 및 유지보수

애플리케이션은 포괄적인 로깅 시스템을 사용합니다:

- 모든 로그는 `logs/` 디렉토리에 저장됩니다
- 로그 파일은 과도한 디스크 사용을 방지하기 위해 자동으로 순환됩니다
- 다양한 구성 요소가 다른 파일에 로깅됩니다:
  - `app.log`: 일반 애플리케이션 로그
  - `api.log`: API 서비스 로그
  - `crawlers.log`: 웹 크롤러 로그
  - `requests.log`: HTTP 요청 로그
  - `error.log`: 모든 구성 요소의 오류 수준 로그

애플리케이션 모니터링:

```bash
# 일반 애플리케이션 로그 보기
tail -f logs/app.log

# 오류 로그 보기
tail -f logs/error.log

# 크롤러 로그 보기
tail -f logs/crawlers.log
```

## 🤝 기여하기

프로젝트 기여는 언제나 환영합니다. 다음 단계를 따라주세요:

1. 프로젝트 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. 풀 리퀘스트 제출

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 👥 팀

| 역할 | 이름 |
|------|------|
| 프로젝트 리더 | 이승헌 |
| 백엔드 개발자 | 김가람 |
| 프론트엔드 개발자 | 박준혁 |
| AI 엔지니어 | 윤수혁 |

## 📬 연락처

문의 사항은 다음 주소로 연락주세요:  
cvfactory.team@gmail.com 