import os
from pathlib import Path
import dj_database_url # Add import

# Read ALLOWED_HOSTS from environment variable 'ALLOWED_HOSTS', default to local hosts
allowed_hosts_str = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1') # Use ALLOWED_HOSTS
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]

# Read CORS_ALLOWED_ORIGINS from environment variable, default to local dev server
cors_origins_str = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]

# Read CSRF_TRUSTED_ORIGINS from environment variable, default to local dev server
csrf_origins_str = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_str.split(',') if origin.strip()]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = '/app/staticfiles/'
STATIC_URL = '/static/' # URL to serve static files from

STATICFILES_DIRS = [
    BASE_DIR,
] # Add BASE_DIR to find static files in the project root

# Quick-start development settings - unsuitable for production
# Read SECRET_KEY from environment variable 'SECRET_KEY', use placeholder only if not set (unsafe for production)
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-placeholder-for-local-development') # Use SECRET_KEY

# Read DEBUG from environment variable 'DEBUG', default to 'True' for local development
DEBUG = os.getenv('DEBUG', 'True') == 'True' # Use DEBUG

# ... existing code ... 

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Static files app
    'corsheaders', # Add corsheaders
    # Add your other apps here
    'core',
]

# Quick-start development settings - unsuitable for production
# ... existing code ... 

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Add CorsMiddleware near the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls' # Changed from main.urls

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR], # Add BASE_DIR to look for templates in the project root
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application' # Changed from main.wsgi.application


# Database
# ... existing code ... 

# Database configuration using dj-database-url
# Default to SQLite in the project root if DATABASE_URL is not set
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
    )
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# ... existing code ... 