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
| Category | Technologies |
|----------|--------------|
| Framework | Django |
| Frontend | HTML, CSS, JavaScript |
| AI/ML | Groq API |
| Deployment | Northflank, Docker |

## 🎉 v1.1 릴리즈 노트

이번 v1.1 릴리즈에는 애플리케이션의 안정성 향상 및 배포 프로세스 개선을 위한 여러 변경 사항이 포함되었습니다. 주요 내용은 다음과 같습니다.

-   **PostgreSQL 데이터베이스 문제 해결:** 공유 메모리 충돌 및 Patroni 종료 관련 로그를 분석하여 데이터베이스 시작 문제를 진단하고 대응했습니다.
-   **Cloudflare 캐싱 일관성 문제 개선:** 배포 후 CSS 등 정적 파일 변경 사항이 즉시 반영되지 않는 문제를 해결하기 위해 Cloudflare API를 이용한 캐시 퍼지 스크립트를 도입하고 배포 프로세스에 통합했습니다. 또한, 캐시 퍼지 작업의 성공/실패 여부를 추적하기 위해 스크립트의 로깅을 강화했습니다.

## 🚀 시작하기

### 필수 요구사항
- Python 3.8+
- uv (Python 패키지 설치 및 관리 도구)
- Git
- Docker (선택 사항, Northflank 배포 시 필요)
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
├── index.html
├── logo.png
├── northflank.json
├── style.css
├── manage.py  # Django 프로젝트 파일이 있다면 추가
├── (앱 디렉토리) # Django 앱 디렉토리
├── requirements.txt # Python 종속성 파일
└── README.md
```
(실제 프로젝트 구조에 맞게 업데이트 필요)

## 📄 라이선스
CC BY-NC 4.0 License
(자세한 내용은 [LICENSE](LICENSE) 파일을 참고하십시오.)

## 📬 문의
wintrover@gmail.com 