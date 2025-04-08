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

1. **`develop` branch**: Integration branch for development work
   - All daily development work happens here
   - Use for testing and integration
   - Only test and build steps are executed when pushing to this branch

2. **`production` branch**: Production-ready code only
   - Merge to production only when ready to deploy
   - Pushing to production automatically triggers deployment to Render.com
   - Helps control when and where deployments occur

### Development Workflow Guidelines

1. **Development Phase**
   ```bash
   git checkout develop
   # Make your changes
   git add .
   git commit -m "Feature implementation"
   git push origin develop
   ```
   - This triggers tests and builds but no deployment

2. **Deployment Phase**
   ```bash
   git checkout production
   git merge develop
   git push origin production
   ```
   - This triggers tests, builds, and automatic deployment
   
3. **Return to Development**
   ```bash
   git checkout develop
   ```

### Security Notes

- Keep all sensitive information in GitHub Secrets, never in the code
- Always include `.env` files in `.gitignore`
- Only push stable code to the production branch
- Regularly check GitHub Actions logs for any issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.