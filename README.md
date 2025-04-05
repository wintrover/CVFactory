# CVFactory

<div align="center">
  <img src="static/images/logo.png" alt="CVFactory Logo" style="width:200px; height:auto;"/>
  <br>
  
  [![English](https://img.shields.io/badge/language-English-blue.svg)](README.md) [![한국어](https://img.shields.io/badge/language-한국어-red.svg)](README.ko.md)
</div>

## 📖 Overview
CVFactory is an automated resume and cover letter generation system for job seekers. It creates personalized cover letters based on job postings and applicant information using AI.

## ✨ Key Features

- **📄 Job Posting Crawler**: Automatically collects relevant job information when a recruitment site URL is entered
- **🏢 Company Information Crawler**: Gathers company vision, mission, values, and other information through the company website URL
- **📝 Customized Cover Letter Generation**: Automatically generates personalized cover letters using Groq API

## 🚀 Installation and Setup

### Local Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CVFactory.git
cd CVFactory
```

2. Set up virtual environment and install packages:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Environment variable setup:
   - Create a `.env` file from `.env.example` and configure settings
   - Set up the Groq API key in your environment variables

4. Database migration:
```bash
python manage.py migrate
```

5. Run server:
```bash
python manage.py runserver
```

6. Access in browser at `http://127.0.0.1:8000`

### Running with Docker

1. Clone the repository and build/run Docker container:
```bash
git clone https://github.com/yourusername/CVFactory.git
cd CVFactory
docker-compose up --build
```

2. Access in browser at `http://localhost:8000`

## 📁 Project Structure

```
CVFactory/
├── api/                # API logic and Groq service
├── crawlers/           # Job posting and company info crawling modules
├── cvfactory/          # Project configuration files
├── data_management/    # User data management module
├── frontend/           # Frontend files
├── logs/               # Log file directory
├── myapp/              # Main app module
├── static/             # Static files
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── manage.py           # Django management script
├── requirements.txt    # Dependency package list
└── README.md           # Project description
```

## 🛠 Technology Stack

### Backend
- **Django**: Web backend framework
- **Django REST Framework**: RESTful API implementation
- **Groq API**: AI-based cover letter generation
- **Selenium**: Web crawling automation
- **BeautifulSoup**: HTML parsing

### Frontend
- **HTML/CSS/JavaScript**: Basic UI implementation
- **Bootstrap**: Responsive design

### Deployment and Development Environment
- **Docker**: Containerization and development
- **Git**: Version control
- **Render.com**: Cloud hosting platform
- **GitHub Actions**: CI/CD automation

### 🚢 Deployment with Render.com

This project is configured for deployment to Render.com. The deployment process is automated using GitHub Actions.

1. Create accounts and services on Render.com:
   - Sign up for Render.com if you don't have an account
   - Create a new Web Service for each environment (development and production)
   - Link your GitHub repository

2. Set up environment variables in Render.com dashboard:
   - All required environment variables mentioned in the `.env.example` file
   - Add your Groq API key and other secrets

3. Deployment happens automatically when code is pushed to:
   - `develop` branch (development environment)
   - `main` branch (production environment)

### 🔄 CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

1. **Testing**: Runs Django tests to ensure code quality
2. **Building**: Prepares the application for deployment
3. **Deployment**: Automatically deploys to Render.com when tests pass

To view the CI/CD configuration, check the `.github/workflows/ci-cd.yml` file.

To set up CI/CD with GitHub Actions:
1. Add the following secrets to your GitHub repository:
   - `RENDER_API_KEY`: Your Render.com API key
   - `RENDER_DEV_SERVICE_ID`: The service ID for your development environment
   - `RENDER_PROD_SERVICE_ID`: The service ID for your production environment
   - All environment variables needed for your application

For more details on deployment configuration, see the `render.yaml` file.

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/job-crawler/` | POST | Crawl job posting from URL |
| `/api/company-info/` | POST | Retrieve company information |
| `/api/generate-letter/` | POST | Generate cover letter |
| `/api/user-letters/` | GET | Get user's saved letters |
| `/api/user-profile/` | GET/PUT | Get or update user profile |

## 🔧 Environment Configuration

This project uses environment variables for configuration. Follow these steps to set up your environment:

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file and set appropriate values for your environment:
   - Set `DEBUG=True` for development, `DEBUG=False` for production
   - Configure `ALLOWED_HOSTS` with your domain names
   - Add your Google OAuth credentials
   - Set your Groq API key
   - Configure security settings as needed

In Docker environments, these variables are automatically loaded from the `.env` file.

## 📄 License

This project is distributed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0). This means:

- You are free to share and adapt the material for non-commercial purposes as long as you give appropriate credit.
- You may NOT use this material for commercial purposes.

See the `LICENSE` file for details or visit [Creative Commons BY-NC 4.0](http://creativecommons.org/licenses/by-nc/4.0/).

## 📬 Contact

For inquiries, please contact:  
wintrover@gmail.com
