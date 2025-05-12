import os
from pathlib import Path

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = '/app/staticfiles/'
STATIC_URL = '/static/' # URL to serve static files from

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