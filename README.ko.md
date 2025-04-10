# CVFactory

<div align="center">
  <img src="docs/images/logo.png" alt="CVFactory 로고" style="width:200px; height:auto;"/>
  <br>
  
  [![English](https://img.shields.io/badge/language-English-blue.svg)](README.md) [![한국어](https://img.shields.io/badge/language-한국어-red.svg)](README.ko.md)
</div>

## 📖 개요
CVFactory는 구직자를 위한 맞춤형 자기소개서 자동 생성 시스템입니다. AI 기술을 활용하여 채용 공고와 지원자 정보를 분석해 개인화된 자기소개서를 생성합니다. 빠르고 효율적인 취업 준비를 원하는 구직자들을 위한 최적의 솔루션입니다.

## 🌐 라이브 데모
[cvfactory.dev](https://cvfactory.dev)에서 실제 작동하는 애플리케이션을 체험해보세요.

## ✨ 주요 기능
- **📄 채용 공고 크롤링**: 채용 사이트 URL 입력 시 관련 정보 자동 수집
- **🏢 기업 정보 크롤링**: 기업 홈페이지에서 비전, 미션, 가치관 등 정보 자동 수집
- **📝 맞춤형 자기소개서 생성**: Groq API 기반 개인화된 자기소개서 생성

## 🛠️ 기술 스택

### 백엔드
- **프레임워크**: Django, Django REST Framework
- **인공지능**: Groq API (LLM 기반 텍스트 생성)
- **크롤링**: Selenium, BeautifulSoup
- **데이터베이스**: SQLite(개발), PostgreSQL(배포)
- **서버**: Gunicorn WSGI 서버

### 프론트엔드
- **기본 기술**: HTML5, CSS3, JavaScript(ES6+)
- **UI 프레임워크**: Bootstrap 5
- **애니메이션**: Lottie

### 배포 및 인프라
- **컨테이너화**: Docker, Docker Compose
- **클라우드 호스팅**: Render.com
- **버전 관리**: Git, GitHub

## 🏗️ 아키텍처

### 소프트웨어 구조
```
CVFactory/
├── api/                # API 로직 및 Groq 서비스 통합
├── crawlers/           # 채용 정보 및 기업 정보 크롤링 모듈
├── frontend/           # 사용자 인터페이스 요소
├── docker/             # 도커 환경 구성 파일
├── myapp/              # 주요 Django 앱
├── logs/               # 로그 파일 저장소
├── scripts/            # 유틸리티 스크립트
└── static_dev/static_prod/ # 정적 파일 (개발/배포용)
```

### 핵심 모듈
- **크롤링 엔진**: `Job_Post_Crawler.py`, `Target_Company_Crawler.py`
- **AI 서비스**: `groq_service.py` (Groq API 연동)
- **웹 프론트엔드**: `frontend/` 디렉토리 내 파일들

## 🔒 보안 아키텍처

### 데이터 보호
- **민감 정보 관리**: 환경 변수(.env) 기반 설정
- **HTTPS 적용**: 모든 통신 암호화
- **API 키 보호**: 서버 측 저장 및 관리

### 인증 및 권한
- **API 보안**: 토큰 기반 인증
- **CSRF 보호**: Django 내장 CSRF 토큰 활용
- **CORS 정책**: 허용된 출처만 접근 가능

### 로깅 및 모니터링
- **보안 로그**: `security.log`에 인증 및 권한 이벤트 기록
- **환경별 로깅**: 개발/배포 환경에 따른 차별화된 로깅 전략

## 🔄 데이터 파이프라인

```
[사용자 입력] → [크롤링 엔진] → [데이터 가공] → [AI 분석] → [문서 생성] → [결과 표시]
```

1. **데이터 수집 단계**: 채용 정보 및 기업 정보 크롤링
2. **분석 단계**: 수집된 정보 구조화 및 핵심 요소 추출
3. **생성 단계**: AI 기반 자기소개서 초안 작성
4. **최적화 단계**: 맞춤형 스타일 및 강조점 적용
5. **전달 단계**: 사용자에게 결과물 제공

## 🔌 API 구조

### 내부 API 엔드포인트
| 엔드포인트 | 메소드 | 설명 |
|----------|--------|-------------|
| `/api/job-crawler/` | POST | 채용 공고 크롤링 |
| `/api/company-info/` | POST | 기업 정보 수집 |
| `/api/generate-letter/` | POST | 자기소개서 생성 |

### 외부 API 통합
- **Groq API**: 텍스트 생성 및 분석

## 👤 사용자 흐름

### 자기소개서 생성
```
[채용공고 URL 입력] → [기업정보 확인] → [자기소개서 생성] → [결과 확인]
```

## ⚙️ 개발 및 배포 환경

### 로컬 개발 환경 설정
```bash
# 레포지토리 클론
git clone https://github.com/yourusername/CVFactory.git
cd CVFactory

# Conda 가상환경 설정
conda create -n cvfactory python=3.9
conda activate cvfactory
pip install -r requirements.txt

# 환경 변수 설정
# .env.example를 .env로 복사하고 필요한 값 설정

# 개발 서버 실행
python manage.py migrate
python manage.py runserver
```

### Docker 개발 환경
```bash
cd 'D:\Coding\CVFactory'
docker-compose -f docker/docker-compose.dev.yml up --build
```

### 배포 환경
- CI/CD 워크플로우 구성됨

## 📊 모니터링 및 로깅

### 모니터링 지표
- **API 응답 시간**: 성능 측정
- **에러율**: 시스템 안정성 평가
- **사용자 활동**: 기능별 사용 패턴 분석

## 👥 팀원 구성

| 역할 | 이름 |
|------|------|
| 기획 및 프로젝트 리더 | 윤수혁 |
| 백엔드 및 API | 류양환 |
| 프론트엔드 및 UI/UX | 신동찬 |
| 크롤링 모델러 | 문이환 |

## 📄 라이센스
이 프로젝트는 Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)를 따릅니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 👨‍💻 기여하기
이슈 제출, 풀 리퀘스트, 문서 개선 등 모든 형태의 기여를 환영합니다. 기여하기 전에 기여 가이드라인을 확인해주세요.

## 📬 연락처
문의사항이 있으시면 wintrover@gmail.com으로 연락해주세요. 