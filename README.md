# CVFactory - AI Cover Letter Generator

<div align="center">
  <img src="logo.png" alt="CVFactory Logo" style="width:200px; height:auto;"/>
  <br>

  [![한국어](https://img.shields.io/badge/language-한국어-red.svg)](README.kr.md)
</div>

## 📖 Overview
CVFactory is a Django web application that generates personalized cover letters based on job posting URLs, company URLs, and user-provided stories.

## ✨ Key Features
- Input job posting URL and company URL
- Provide personal stories and details
- Generate personalized cover letters using AI

## 🛠 Tech Stack
| Category | Technologies |
|----------|--------------|
| Framework | Django |
| Frontend | HTML, CSS, JavaScript |
| AI/ML | Groq API |
| Deployment | Northflank, Docker |

## 🚀 Getting Started

### Prerequisites
- Python 3.x (Conda recommended)
- Docker
- Docker Compose

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd CVFactory
   ```
   (Replace `<repository_url>` with the actual repository URL.)

2. **Conda environment setup:**
   ```bash
   conda create -n cvfactory python=3.x
   conda activate cvfactory
   ```
   (Replace Python 3.x with the specific version listed in `requirements.txt` or a suitable version like 3.9/3.10.)

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server:**

   * **Using Django's development server:**
     ```bash
     python manage.py runserver
     ```
   * **Using Docker Compose:**
     Run the following command from the project root directory:
     ```bash
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
This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License. See the [LICENSE](LICENSE) file for details.

## 📬 Contact
wintrover@gmail.com 