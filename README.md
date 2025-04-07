# CVFactory

<div align="center">
  <img src="static/images/logo.png" alt="CVFactory Logo" style="width:200px; height:auto;"/>
  <br>
  
  [![English](https://img.shields.io/badge/language-English-blue.svg)](README.md) [![한국어](https://img.shields.io/badge/language-한국어-red.svg)](README.ko.md)
</div>

## 📖 Overview
CVFactory is an automated resume and cover letter generation system for job seekers. It creates personalized cover letters based on job postings and applicant information using AI. The system analyzes job descriptions and company information to highlight relevant skills and experiences in the generated documents.

## 🌐 Live Demo

You can see the live application in action at **[cvfactory.dev](https://cvfactory.dev)**

Experience the full functionality of CVFactory and generate your own personalized cover letters and resumes in minutes!

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
- **GitHub Actions**: CI/CD automation
- **Render.com**: Cloud hosting platform (optional)

## 🔄 Environment Switching

This project supports both development and production environments. Use the provided scripts to switch between them:

```bash
# Switch to development environment (default)
./switch_env.sh development  # Linux/macOS
.\switch_env.bat development  # Windows

# Switch to production environment
./switch_env.sh production  # Linux/macOS
.\switch_env.bat production  # Windows
```

## 🚢 CI/CD Pipeline with GitHub Actions

This project uses GitHub Actions for continuous integration and deployment:

1. **Environment Debugging**: Verifies environment settings and creates reports
2. **Testing**: Runs Django tests to ensure code quality
3. **Building**: Prepares the application for deployment
4. **Deployment**: Automatically deploys based on branch (develop or main)

To view the CI/CD configuration, check the `.github/workflows/ci-cd.yml` file.

### GitHub Branch Strategy

We use a simple and effective branching strategy to optimize development workflow and manage deployment costs:

1. **`feature/feature-name` branches**: Used for individual feature development
   - Create these branches from `develop` branch
   - Use for daily coding tasks and work-in-progress changes
   - Merge back to `develop` when feature is complete

2. **`develop` branch**: Integration branch for completed features
   - All completed feature branches get merged here
   - Use for testing and integration
   - No Render pipelines are triggered on this branch

3. **`production` branch**: Production-ready code only
   - Merge to production only when ready to deploy
   - Pushing to production automatically triggers Render deployment
   - Helps minimize pipeline usage costs

#### Development Workflow

```bash
# Start a new feature
git checkout develop
git checkout -b feature/your-feature-name

# Make changes and commit to feature branch
git add .
git commit -m "Your changes"
git push origin feature/your-feature-name

# When feature is complete, merge to develop
git checkout develop
git merge feature/your-feature-name
git push origin develop  # No deployment triggered

# When ready to deploy
git checkout production
git merge develop
git push origin production  # Triggers Render deployment
git checkout develop  # Return to develop branch
```

This approach allows frequent commits during development while controlling when deployments occur.

### Setting up CI/CD

To set up CI/CD with GitHub Actions, add the following secrets to your GitHub repository:

1. **Deployment Credentials**
   - `RENDER_API_KEY`: Your Render.com API key
   - `RENDER_DEV_SERVICE_ID`: The service ID for your development environment
   - `RENDER_PROD_SERVICE_ID`: The service ID for your production environment

2. **Environment Variables**
   - `DJANGO_SECRET_KEY`: Django security key
   - `ALLOWED_HOSTS`: Allowed hosts list (comma-separated)
   - `GOOGLE_CLIENT_ID`: Google OAuth client ID