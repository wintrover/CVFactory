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
- **크롤링**: Playwright (비동기, headless, 네트워크 감지)
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
└── static/ # 정적 파일 (개발용)
└── static_prod/ # 정적 파일 (배포용)
```

### 핵심 모듈
- **크롤링 엔진**: `utils/playwright_crawler.py` (공통 크롤링 유틸)
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

### Azure Computer Vision API 설정
채용공고 이미지에서 텍스트를 추출하기 위해 Microsoft Azure Computer Vision API를 사용합니다.

1. [Azure Portal](https://portal.azure.com/)에 가입하고 로그인
2. [Azure Computer Vision 리소스 생성](https://portal.azure.com/#create/Microsoft.CognitiveServicesComputerVision)
3. 리소스 그룹, 지역, 이름 등을 설정하고 F0(무료) 가격 계층 선택
4. 생성 후 리소스로 이동하여 '키 및 엔드포인트' 메뉴에서 정보 확인
5. `.env` 파일에 아래 환경 변수 추가:
   ```
   AZURE_VISION_KEY=발급받은_API_키
   AZURE_VISION_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
   ```

### Docker 개발 환경
```bash
cd 'D:\Coding\CVFactory'
docker-compose -f docker/docker-compose.dev.yml up --build
```

### 배포 환경
- **Render.com**: `production` 브랜치에서 수동 배포

## 브랜치 전략
- **develop**: 개발 및 테스트용
- **production**: 운영 서버 배포용

## 📊 모니터링 및 로깅

### 로그 구조
- **개발 환경**: 상세 디버그 로그, SQL 쿼리 로깅
- **배포 환경**: 에러 및 중요 이벤트 중심 로깅

### 모니터링 지표
- **API 응답 시간**: 성능 측정
- **에러율**: 시스템 안정성 평가
- **사용자 활동**: 기능별 사용 패턴 분석

## SEO 설정 가이드

CVFactory는 다음과 같은 SEO 최적화가 적용되어 있습니다:

1. **메타 태그**: 검색 엔진이 사이트 내용을 이해할 수 있도록 메타 태그를 추가했습니다.
2. **구조화된 데이터(JSON-LD)**: Schema.org 마크업을 통해 검색 엔진에 더 많은 정보를 제공합니다.
3. **사이트맵**: 검색 엔진 크롤러가 모든 페이지를 찾을 수 있도록 사이트맵을 생성합니다.
4. **robots.txt**: 크롤러의 접근 제어를 위한 설정입니다.
5. **URL 구조 최적화**: 사용자와 검색 엔진이 이해하기 쉬운 URL 구조를 유지합니다.
6. **SSR 지원**: django-seo-js를 통해 자바스크립트 콘텐츠의 SEO 최적화를 지원합니다.
7. **Cloudflare CDN**: 성능 최적화 및 캐싱을 통한 로딩 속도 개선으로 SEO 점수를 향상시킵니다.

### Prerender.io 설정

Prerender.io 서비스를 사용하려면 다음 절차를 따르세요:

1. Prerender.io 계정 생성: https://prerender.io/
2. 발급받은 토큰을 `settings.py`의 `SEO_JS_PRERENDER_TOKEN` 값으로 설정
3. 프로덕션 환경에서 `SEO_JS_ENABLED = True` 확인

### 새 페이지 추가 시 SEO 설정

새 페이지를 추가할 때 다음 항목을 확인하세요:

1. 적절한 `<title>` 태그와 메타 설명 추가
2. 페이지에 맞는 구조화된 데이터(JSON-LD) 추가
3. 사이트맵에 페이지 추가
4. 페이지 내 적절한 헤딩 구조(h1, h2 등) 사용
5. 이미지에 alt 태그 추가 

## 🚀 크롤링 엔진 (Playwright 기반)

모든 크롤링, 네트워크, 이미지 추출은 Playwright 기반 비동기 유틸로 통일되어 있습니다.

### 주요 함수

- `crawl_page(url, ...)`: 단일 페이지 크롤링 (브라우저 위장, 네트워크 로그, 내부 링크 추출)
- `crawl_site_recursive(start_url, max_depth=2, ...)`: 내부 링크를 따라 재귀적으로 크롤링 (최대 깊이 지정)

### 사용 예시

```python
import asyncio
from utils.playwright_crawler import crawl_page, crawl_site_recursive

# 단일 페이지 크롤링
result = asyncio.run(crawl_page("https://example.com"))

# 사이트 전체(내부 링크 재귀) 크롤링
results = asyncio.run(crawl_site_recursive("https://example.com", max_depth=2))
```

- 모든 네트워크 요청/응답(이미지, JS, CSS, XHR 등) 자동 기록
- User-Agent, navigator.webdriver, 언어, 타임존 등 브라우저 위장 적용
- HTML, 네트워크 로그, 내부 링크 반환

> **참고:** 기존 Selenium/requests 기반 크롤링 코드는 모두 제거되었습니다. 크롤링 및 네트워크 캡처는 반드시 Playwright 유틸만 사용하세요. 

## 📄 라이센스
이 프로젝트는 MIT 라이센스를 따릅니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 👨‍💻 기여하기
이슈 제출, 풀 리퀘스트, 문서 개선 등 모든 형태의 기여를 환영합니다. 기여하기 전에 기여 가이드라인을 확인해주세요.

## 📬 연락처
문의사항이 있으시면 wintrover@gmail.com으로 연락해주세요. 