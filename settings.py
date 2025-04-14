import os

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,https://cvfactory.dev').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,https://cvfactory.dev,https://*.cvfactory.dev').split(',')
STATIC_URL = 'https://cvfactory.dev/static/' 