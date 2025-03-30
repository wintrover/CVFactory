# CVFactory

*Read this in [Korean](README.ko.md)*

CVFactory is an automated resume and cover letter generation system for job seekers. It creates personalized cover letters based on job postings and applicant information using AI.

## Key Features

- **Job Posting Crawler**: Automatically collects relevant job information when a recruitment site URL is entered
- **Company Information Crawler**: Gathers company vision, mission, values, and other information through the company website URL
- **Customized Cover Letter Generation**: Automatically generates personalized cover letters using Groq API
- **Logging System**: Records server requests and responses, API calls, errors, etc. in log files

## Installation and Setup

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
   - Create a `secretkey.env` file and set the Django security key
   - Set up the Groq API key in the `groq.env` file

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

## Project Structure

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

## Technology Stack

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
- **Docker**: Containerization and deployment
- **Git**: Version control

## Contributing

Contributions to the project are always welcome. Please follow these steps:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Submit a pull request

## License

This project is distributed under the MIT license. See the `LICENSE` file for details.

## Environment Configuration

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

## Logging and Maintenance

The application uses a comprehensive logging system:

- All logs are stored in the `logs/` directory
- Log files are automatically rotated to prevent excessive disk usage
- Different components log to different files:
  - `app.log`: General application logs
  - `api.log`: API service logs
  - `crawlers.log`: Web crawler logs
  - `requests.log`: HTTP request logs
  - `error.log`: Error-level logs from all components

To monitor the application:

```bash
# View general application logs
tail -f logs/app.log

# View error logs
tail -f logs/error.log

# View crawler logs
tail -f logs/crawlers.log
```
