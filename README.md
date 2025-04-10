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
- **💾 Document Management**: Save, edit, and download generated documents
- **👤 User Profiles**: Google account integration and profile management

## 🛠️ Technology Stack

### Backend
- **Framework**: Django, Django REST Framework
- **AI**: Groq API (LLM-based text generation)
- **Web Crawling**: Selenium, BeautifulSoup
- **Authentication**: Google OAuth
- **Database**: SQLite(development), PostgreSQL(production)
- **Server**: Gunicorn WSGI Server

### Frontend
- **Core Technologies**: HTML5, CSS3, JavaScript(ES6+)
- **UI Framework**: Bootstrap 5
- **Animation**: Lottie

### Deployment & Infrastructure
- **Containerization**: Docker, Docker Compose
- **Cloud Hosting**: Render.com
- **CI/CD**: GitHub Actions
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
- **User Authentication**: Google OAuth 2.0
- **API Security**: Token-based authentication
- **CSRF Protection**: Django built-in CSRF tokens
- **CORS Policy**: Only allowed origins can access

### Logging & Monitoring
- **Security Logs**: Authentication and authorization events recorded in `security.log`
- **Environment-specific Logging**: Different logging strategies for development/production

## 🔄 Data Pipeline

```
[User Input] → [Crawling Engine] → [Data Processing] → [AI Analysis] → [Document Generation] → [User Repository]
```

1. **Data Collection Stage**: Job information and company information crawling
2. **Analysis Stage**: Structuring collected information and extracting key elements
3. **Generation Stage**: AI-based cover letter draft creation
4. **Optimization Stage**: Applying customized style and emphasis points
5. **Delivery Stage**: Providing results to users and saving

## 🔌 API Structure

### Internal API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/job-crawler/` | POST | Job posting crawling |
| `/api/company-info/` | POST | Company information collection |
| `/api/generate-letter/` | POST | Cover letter generation |
| `/api/user-letters/` | GET/POST | User document management |
| `/api/user-profile/` | GET/PUT | User profile management |

### External API Integration
- **Groq API**: Text generation and analysis
- **Google OAuth API**: User authentication

## 👤 User Flow

### Registration & Login
```
[First Visit] → [Google Login] → [Profile Setup] → [Dashboard]
```

### Cover Letter Generation
```
[Job Posting URL Input] → [Company Info Confirmation] → [Cover Letter Generation] → [Review & Edit] → [Save/Download]
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
- **Render.com**: Automatic deployment when pushing to `production` branch
- **Environment Switching**: Scripts provided for switching between development/production

## 🚢 CI/CD Pipeline

### GitHub Actions Configuration
```
[Code Push] → [Test] → [Build] → [Deploy (production branch only)]
```

### Branch Strategy
- **develop**: For development and testing (not deployed)
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
