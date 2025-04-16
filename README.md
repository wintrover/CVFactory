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
└── static/ # Static files (development)
└── static_prod/ # Static files (production)
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
- **Render.com**: Manual deployment from `production` branch

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

## SEO Configuration Guide

CVFactory has the following SEO optimizations applied:

1. **Meta Tags**: Added meta tags to help search engines understand the site content.
2. **Structured Data (JSON-LD)**: Provides additional information to search engines through Schema.org markup.
3. **Sitemap**: Generated to help search engine crawlers find all pages.
4. **robots.txt**: Controls crawler access to different areas of the site.
5. **URL Structure Optimization**: Maintains user and search engine-friendly URL structures.
6. **SSR Support**: Supports SEO optimization for JavaScript content through django-seo-js.
7. **Cloudflare CDN**: Performance optimization and improved loading speed via caching to enhance SEO scores.

### Prerender.io Setup

Follow these steps to use the Prerender.io service:

1. Create a Prerender.io account: https://prerender.io/
2. Set the token you received as the `SEO_JS_PRERENDER_TOKEN` value in `settings.py`
3. Ensure `SEO_JS_ENABLED = True` in the production environment

### SEO Settings When Adding New Pages

When adding new pages, check the following items:

1. Add appropriate `<title>` tags and meta descriptions
2. Add structured data (JSON-LD) relevant to the page
3. Add the page to the sitemap
4. Use proper heading structure (h1, h2, etc.) within the page
5. Add alt tags to images
