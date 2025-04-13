# CVFactory

<div align="center">
  <img src="docs/images/logo.png" alt="CVFactory Logo" style="width:200px; height:auto;"/>
  <br>
  
  [![English](https://img.shields.io/badge/language-English-blue.svg)](README.md) [![한국어](https://img.shields.io/badge/language-한국어-red.svg)](README.ko.md)
</div>

## 📖 Overview
CVFactory is an automated resume and cover letter generation system for job seekers. It creates personalized documents based on job postings and applicant information using AI. The system analyzes job descriptions and company information to highlight relevant skills and experiences.

## 🌐 Live Demo
Experience the application at [cvfactory.dev](https://cvfactory.dev).

## ✨ Key Features
- **📄 Job Posting Crawler**: Automatically collects job information from recruitment site URLs
- **🏢 Company Information Crawler**: Gathers company vision, mission, and values from company websites
- **📝 Custom Cover Letter Generation**: Creates personalized cover letters using Groq API

## 🛠️ Technology Stack

### Backend
- **Framework**: Django, Django REST Framework
- **AI**: Groq API (LLM-based text generation)
- **Web Crawling**: Selenium, BeautifulSoup
- **Database**: SQLite(development), PostgreSQL(production)
- **Server**: Gunicorn WSGI Server

### Frontend
- **Core Technologies**: HTML5, CSS3, JavaScript(ES6+)
- **UI Framework**: Bootstrap 5
- **Animation**: Lottie

### Deployment & Infrastructure
- **Containerization**: Docker, Docker Compose
- **Cloud Hosting**: Render.com
- **Version Control**: Git, GitHub

## 🏗️ Architecture

### Software Structure
```
CVFactory/
├── api/                # API logic and Groq service integration
├── crawlers/           # Job posting and company information crawling modules
├── frontend/           # User interface elements
├── docker/             # Docker environment configuration files
├── myapp/              # Main Django app
├── logs/               # Log files storage
├── scripts/            # Utility scripts
└── static_dev/static_prod/ # Static files (development/production)
```

### Core Modules
- **Crawling Engine**: `Job_Post_Crawler.py`, `Target_Company_Crawler.py`
- **AI Service**: `groq_service.py` (Groq API integration)
- **Web Frontend**: Files in the `frontend/` directory

## 🔒 Security Architecture

### Data Protection
- **Sensitive Information Management**: Environment variable (.env) based configuration
- **HTTPS Implementation**: All communications encrypted
- **API Key Protection**: Server-side storage and management

### Authentication & Authorization
- **API Security**: Token-based authentication
- **CSRF Protection**: Django built-in CSRF tokens
- **CORS Policy**: Only allowed origins can access

### Logging & Monitoring
- **Security Logs**: Authentication and authorization events recorded in `security.log`
- **Environment-specific Logging**: Different logging strategies for development/production

## 🔄 Data Pipeline

```
[User Input] → [Crawling Engine] → [Data Processing] → [AI Analysis] → [Document Generation] → [Results Display]
```

1. **Data Collection Stage**: Job information and company information crawling
2. **Analysis Stage**: Structuring collected information and extracting key elements
3. **Generation Stage**: AI-based cover letter draft creation
4. **Optimization Stage**: Applying customized style and emphasis points
5. **Delivery Stage**: Providing results to users

## 🔌 API Structure

### Internal API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/job-crawler/` | POST | Job posting crawling |
| `/api/company-info/` | POST | Company information collection |
| `/api/generate-letter/` | POST | Cover letter generation |

### External API Integration
- **Groq API**: Text generation and analysis

## 👤 User Flow

### Cover Letter Generation
```
[Job Posting URL Input] → [Company Info Confirmation] → [Cover Letter Generation] → [Results Review]
```

## ⚙️ Development & Deployment Environment

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/CVFactory.git
cd CVFactory

# Conda virtual environment setup
conda create -n cvfactory python=3.9
conda activate cvfactory
pip install -r requirements.txt

# Environment variable setup
# Copy .env.example to .env and set necessary values

# Run development server
python manage.py migrate
python manage.py runserver
```

### Docker Development Environment
```bash
cd 'D:\Coding\CVFactory'
docker-compose -f docker/docker-compose.dev.yml up --build
```

### Deployment Environment
- **Render.com**: Deployed on `production` branch

## Branch Strategy
- **develop**: For development and testing
- **production**: For production server deployment

## 📊 Monitoring & Logging

### Log Structure
- **Development Environment**: Detailed debug logs, SQL query logging
- **Production Environment**: Error and important event-focused logging

### Monitoring Metrics
- **API Response Time**: Performance measurement
- **Error Rate**: System stability evaluation
- **User Activity**: Usage pattern analysis by feature

## 📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

## 👨‍💻 Contributing
All forms of contribution are welcome, including issue submission, pull requests, and documentation improvements. Please check the contribution guidelines before contributing.

## 📬 Contact
For any inquiries, please contact wintrover@gmail.com.

## SEO 설정 가이드

CVFactory는 다음과 같은 SEO 최적화가 적용되어 있습니다:

1. **메타 태그**: 검색 엔진이 사이트 내용을 이해할 수 있도록 메타 태그를 추가했습니다.
2. **구조화된 데이터(JSON-LD)**: Schema.org 마크업을 통해 검색 엔진에 더 많은 정보를 제공합니다.
3. **사이트맵**: 검색 엔진 크롤러가 모든 페이지를 찾을 수 있도록 사이트맵을 생성합니다.
4. **robots.txt**: 크롤러의 접근 제어를 위한 설정입니다.
5. **URL 구조 최적화**: 사용자와 검색 엔진이 이해하기 쉬운 URL 구조를 유지합니다.
6. **SSR 지원**: django-seo-js를 통해 자바스크립트 콘텐츠의 SEO 최적화를 지원합니다.
7. **Cloudflare CDN**: Performance optimization and improved loading speed via caching to enhance SEO scores.

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
