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
   - `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
   - `GROQ_API_KEY`: Groq API key
   - `API_KEY`: Backend API authentication key
   - `CSRF_TRUSTED_ORIGINS`: CSRF allowed origins
   - `CORS_ALLOWED_ORIGINS`: CORS allowed origins
   - `DOMAIN_NAME`: Custom domain name (optional)

Branch management:
- `develop` branch: Automatically deploys to development environment
- `main` branch: Automatically deploys to production environment

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

## 📊 Logging Configuration

CVFactory has different logging settings for development and production environments:

### Development Environment Logging
- **Log Level**: DEBUG (all logs recorded)
- **Console Output**: Enabled (for easier debugging)
- **Additional Log Files**:
  - `debug.log`: Detailed debug-level logs
  - `groq_service_debug.log`: API call-related detailed logs
  - `logs/crawling/`: Directory for crawling results
- **SQL Query Logging**: Enabled (for performance optimization)

### Production Environment Logging
- **Log Level**: INFO (only informational logs and above recorded)
- **Console Output**: Disabled
- **Essential Log Files**:
  - `django.log`: General application logs
  - `api.log`: API call-related logs
  - `error.log`: Error-level logs
  - `security.log`: Security-related logs
- **SQL Query Logging**: Disabled

## 🔒 Security Guidelines

For secure operation of CVFactory, follow these security guidelines:

- API keys and sensitive information should never be committed to Git
- Always use HTTPS in production environments
- Adjust logging levels appropriately to prevent logging sensitive information
- Follow the recommendations in `SECURITY_GUIDELINES.md`

### API Security Features

CVFactory implements several security measures to protect API access:

1. **Authentication Required**: All API endpoints require user authentication, except for public endpoints such as login and registration.

2. **Referrer Checking**: API calls are restricted to requests originating from your website domain, preventing unauthorized external access.

3. **Rate Limiting**: Requests are rate-limited to prevent abuse:
   - IP-based rate limiting: Maximum 60 requests per minute
   - User-based rate limiting: Maximum 120 requests per minute for authenticated users

4. **Session Validation**: API requests require a valid session, ensuring only website visitors can use the service.

### API Authentication Example

API endpoints require authentication headers:

```javascript
// API call example
fetch('/api/generate-letter/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': 'your-api-key-here',  // API key header
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify(data)
});
```

## 📄 License

This project is distributed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0). This means:

- You are free to share and adapt the material for non-commercial purposes as long as you give appropriate credit.
- You may NOT use this material for commercial purposes.

See the `LICENSE` file for details or visit [Creative Commons BY-NC 4.0](http://creativecommons.org/licenses/by-nc/4.0/).

## 📬 Contact

For inquiries, please contact:  
wintrover@gmail.com
