# CVFactory

이 프로젝트는 GPT와 크롤링을 활용한 자기소개서 자동 생성 시스템입니다.

## 도커를 사용한 로컬 실행 방법

1. 레포지토리 클론 후 다음 단계를 따릅니다:

```bash
# 프로젝트 디렉토리로 이동
cd CVFactory

# 도커 컨테이너 빌드 및 실행
docker-compose up --build
```

2. 브라우저에서 `http://localhost:8000`으로 접속하여 애플리케이션을 사용할 수 있습니다.

## 기술 스택

- Django: 웹 백엔드 프레임워크
- Django REST Framework: API 구현
- OpenAI API: GPT 기반 자기소개서 생성
- Selenium: 웹 크롤링
- BeautifulSoup: HTML 파싱
- Docker: 컨테이너화 및 배포
