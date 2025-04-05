"""
Django settings for cvfactory project.
"""

from pathlib import Path
import logging.config
import os
from dotenv import load_dotenv
from datetime import timedelta 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드
load_dotenv(dotenv_path=BASE_DIR / ".env")

# 환경변수 로드
load_dotenv()

# 환경변수에서 설정 가져오기
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# API 키 설정 (간단한 API 인증을 위한 옵션)
API_KEY = os.getenv('API_KEY', 'default-dev-api-key-change-in-production')

# Google OAuth 환경 변수
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# 환경 변수가 설정되지 않은 경우 경고 로그 출력
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    import logging
    logger = logging.getLogger('app')
    logger.warning("Google OAuth 자격 증명이 환경 변수로 설정되지 않았습니다. Google 로그인 기능이 작동하지 않을 수 있습니다.")

# 자동 로그인 및 자동 계정 연결 허용
ACCOUNT_ADAPTER = "data_management.adapters.MyAccountAdapter"
SOCIALACCOUNT_ADAPTER = "data_management.adapters.MySocialAccountAdapter"

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_LOGIN_ON_GET = True  

# Application definition
INSTALLED_APPS = [
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework.authtoken", 
    "dj_rest_auth",
    "dj_rest_auth.registration",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    "api",
    "crawlers",
    "myapp",
    "data_management",
    "corsheaders",
]

# CORS 설정
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

AUTH_USER_MODEL = "data_management.User" 

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# 세션 및 쿠키 보안 설정
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 세션 만료 시간 (1시간)

# CSRF 보안 설정
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
CSRF_COOKIE_HTTPONLY = os.getenv('CSRF_COOKIE_HTTPONLY', 'True').lower() == 'true'
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'Lax')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

# 보안 헤더 설정
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS 설정 (배포 환경용)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1년
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # allauth 미들웨어 추가
    "middleware.ApiKeyMiddleware",  # API 키 인증 미들웨어
    "middleware.SecurityHeadersMiddleware",  # 보안 헤더 미들웨어
]

ROOT_URLCONF = "cvfactory.urls"

# 템플릿 디렉토리 설정
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates", BASE_DIR / "frontend"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 정적 파일 설정
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "frontend",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

WSGI_APPLICATION = "cvfactory.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',  
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',  
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# 환경변수에서 로그 레벨 가져오기
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'False').lower() == 'true'
LOG_SQL_QUERIES = os.getenv('LOG_SQL_QUERIES', 'False').lower() == 'true'

# 개발 환경에서 SQL 쿼리 로깅 활성화
if LOG_SQL_QUERIES and DEBUG:
    LOGGING['loggers']['django.db.backends'] = {
        'handlers': ['console', 'debug_file'],
        'level': 'DEBUG',
        'propagate': False,
    }

# 로그 설정 - 환경별 차별화
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'detailed': {
            'format': '=' * 80 + '\n[%(asctime)s] %(levelname)s [%(name)s]\n%(message)s\n' + '=' * 80,
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',  # 개발 환경에서는 DEBUG, 배포 환경에서는 INFO
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'django.log'),
            'maxBytes': 10 * 1024 * 1024 if DEBUG else 5 * 1024 * 1024,  # 개발 환경에서는 10MB, 배포 환경에서는 5MB
            'backupCount': 10 if DEBUG else 5,  # 개발 환경에서는 10개, 배포 환경에서는 5개
            'formatter': 'detailed' if DEBUG else 'verbose',  # 개발 환경에서는 상세 로그
        },
        'api_file': {
            'level': 'DEBUG' if DEBUG else 'INFO',  # 개발 환경에서는 DEBUG, 배포 환경에서는 INFO
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'api.log'),
            'maxBytes': 10 * 1024 * 1024 if DEBUG else 5 * 1024 * 1024,
            'backupCount': 10 if DEBUG else 5,
            'formatter': 'detailed' if DEBUG else 'verbose',
        },
        'security_file': {
            'level': 'INFO',  # 보안 로그는 항상 INFO 이상의 레벨로 설정
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'security.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5MB
            'backupCount': 10,  # 보안 로그는 중요하므로 더 많은 백업 유지
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'error.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'detailed',
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'debug.log'),
            'maxBytes': 20 * 1024 * 1024,  # 디버그 로그는 더 큰 용량
            'backupCount': 10,
            'formatter': 'detailed',
            'filters': ['require_debug_true'],  # 개발 환경에서만 사용
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'api_file', 'error_file', 'debug_file'] if DEBUG else ['api_file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'groq_service': {
            'handlers': ['api_file', 'debug_file'] if DEBUG else ['api_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file', 'console'] if DEBUG else ['security_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'crawlers': {
            'handlers': ['console', 'debug_file'] if DEBUG else ['file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#  Google OAuth 설정 (하드코딩 포함)
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_CLIENT_ID,
            "secret": GOOGLE_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": ["email", "profile", "openid", "https://www.googleapis.com/auth/userinfo.email",
                  "https://www.googleapis.com/auth/userinfo.profile"],
        "AUTH_PARAMS": {
            "access_type": "offline",
            "prompt": "consent",
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# 디버깅용 print 문 제거
# print("Google OAuth 설정 완료")