import os
from pathlib import Path

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'cvfactory.dev']

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = '/app/staticfiles/'
STATIC_URL = '/static/' # URL to serve static files from

STATICFILES_DIRS = [
    BASE_DIR,
] # Add BASE_DIR to find static files in the project root

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-placeholder-for-local-development'

DEBUG = False # Set DEBUG to False for production

# ... existing code ... 

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Static files app
    # Add your other apps here
]

# Quick-start development settings - unsuitable for production
# ... existing code ... 

MIDDLEWARE = [
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