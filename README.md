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
| AI/ML | Groq API |
| Deployment | Northflank, Docker |

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- Git
- Docker (Optional, required for Northflank deployment)
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

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt  # Run if requirements.txt exists
   # Or install necessary libraries individually (e.g., pip install django)
   ```

4. **Migrate database (if using Django):**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server:**
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
├── index.html
├── logo.png
├── northflank.json
├── style.css
├── manage.py  # Add if Django project files exist
├── (app_directory) # Django app directory
├── requirements.txt # Python dependencies file
└── README.md
```
(Update according to your actual project structure)

## 📄 License
CC BY-NC 4.0 License
(See the [LICENSE](LICENSE) file for the full text.)

## 📬 Contact
wintrover@gmail.com 