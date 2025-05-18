# CVFactory - AI Cover Letter Generator

<div align="center">
  <img src="logo.png" alt="CVFactory Logo" style="width:200px; height:auto;"/>
  <br>

  [![한국어](https://img.shields.io/badge/language-한국어-red.svg)](README.kr.md)
</div>

## 📖 Overview
CVFactory is an AI-powered web application that helps users easily generate customized cover letters based on job postings and their personal stories.

## ✨ Key Features
- Extract information based on job posting URL and official company URL
- User story input and analysis
- AI-based draft cover letter generation using input information
- Function to view and edit generated cover letters

## 🛠 Tech Stack
| Category | Technologies |
|----------|--------------|
| Framework | Django |
| Frontend | HTML, CSS, JavaScript |
| AI/ML | Gemini 2.5 Flash API |
| Database | SQLite (development), PostgreSQL (production via dj-database-url) |
| Web Server | Gunicorn |
| Static Files | Whitenoise |
| HTTP Client | Requests |
| Environment Variables | python-dotenv |
| Deployment | Northflank, Docker, Docker Compose, Cloudflare (for caching) |

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- uv (Python package installer and manager)
- Git
- Docker (Optional, required for containerized deployment)
- Conda (Recommended for virtual environment management)

### Installation and Running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wintrover/CVFactory.git
   cd CVFactory
   ```

2. **Set up and activate Conda environment:**
   ```bash
   conda create -n cvfactory python=3.8
   conda activate cvfactory
   ```

3. **Install uv (if not already installed):**
   ```bash
   # Refer to the official uv documentation for installation methods:
   # https://github.com/astral-sh/uv#installation
   # Example using pipx:
   # pipx install uv
   ```

4. **Install dependencies using uv:**
   ```bash
   uv pip install -r requirements.txt  # Run if requirements.txt exists
   # Or install necessary libraries individually (e.g., uv pip install django)
   ```

5. **Migrate database (if using Django):**
   ```bash
   python manage.py migrate
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

   Access the application in your browser at `http://127.0.0.1:8000/` (or the configured port).

### Build and Run with Docker (Optional)

If your project includes a Dockerfile, you can build and run it using the following commands:

```bash
# Build the Docker image
docker build -t cvfactory .

# Run the Docker container
docker run -p 8000:8000 cvfactory
```

## 🐳 Northflank Deployment
You can deploy this project using Northflank. Refer to the Northflank documentation for detailed instructions on setting up and deploying with Northflank.

## 📁 Project Structure
```
CVFactory/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Local development/testing with Docker Compose
├── northflank.json        # Northflank deployment configuration
├── purge_cloudflare_cache.py # Script to purge Cloudflare cache
├── LICENSE                # Project license (CC BY NC 4.0)
├── README.md              # English README
├── README.kr.md           # Korean README
├── index.html             # Main HTML file
├── style.css              # Main CSS file
├── script.js              # Main JavaScript file
├── db.sqlite3             # Default SQLite database file (development)
├── config/                # Django project settings, URLs, WSGI/ASGI
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── __init__.py
└── core/                  # Django core application (views)
    ├── views.py
    └── __init__.py
```

## 📄 License
CC BY-NC 4.0 License
(See the [LICENSE](LICENSE) file for the full text.)

## 📬 Contact
wintrover@gmail.com 