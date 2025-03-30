# CVFactory

CVFactory는 구직자를 위한 맞춤형 자기소개서 자동 생성 시스템입니다. 채용 공고와 지원자 정보를 기반으로 AI가 개인화된 자기소개서를 생성합니다.

## 주요 기능

- **채용 공고 크롤링**: 채용 사이트 URL을 입력하면 관련 채용 정보를 자동으로 수집
- **기업 정보 크롤링**: 기업 홈페이지 URL을 통해 기업의 비전, 미션, 가치관 등 정보 수집
- **맞춤형 자기소개서 생성**: Groq API를 활용하여 개인화된 자기소개서 자동 생성
- **로깅 시스템**: 서버 요청 및 응답, API 호출, 오류 등을 로그 파일에 기록

## 설치 및 실행 방법

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

## 프로젝트 구조

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

## 기술 스택

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

## 기여하기

프로젝트 기여는 언제나 환영합니다. 다음 단계를 따라주세요:

1. 프로젝트 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. 풀 리퀘스트 제출

## 라이센스

이 프로젝트는 GPL-3.0 라이센스 하에 배포됩니다. 자세한 내용은 `COPYING` 파일을 참조하세요.
