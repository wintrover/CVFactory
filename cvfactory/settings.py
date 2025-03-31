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
load_dotenv(dotenv_path=BASE_DIR / "secretkey.env")

# 환경 변수 로드 실패 시 기본값 (하드코딩)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-7q@k&$)+32d7r8nvr!sy3em4y^m19)58yf8)&_je+e&2f)parw")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,0.0.0.0").split(",")

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

# CSRF 설정
CSRF_USE_SESSIONS = os.getenv("CSRF_USE_SESSIONS", "False") == "True"
CSRF_COOKIE_HTTPONLY = os.getenv("CSRF_COOKIE_HTTPONLY", "False") == "True" 
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False" if DEBUG else "True") == "True"
CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "None" if DEBUG else "Lax")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000").split(",")

# CORS 설정
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "True" if DEBUG else "False") == "True"
CORS_ALLOW_CREDENTIALS = True  # 인증된 요청 허용
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",") if not CORS_ALLOW_ALL_ORIGINS else []

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



MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
]

# CSRF 미들웨어는 환경 변수로 제어 (개발 중에는 비활성화 가능)
if os.getenv("ENABLE_CSRF_MIDDLEWARE", "True") == "True":
    MIDDLEWARE.append("django.middleware.csrf.CsrfViewMiddleware")

# 나머지 미들웨어 추가
MIDDLEWARE += [
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",  # 로깅을 위해 추가
    "allauth.account.middleware.AccountMiddleware",  # django-allauth 미들웨어 추가
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
STATIC_URL = "/static/"

if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / "frontend"]
else:
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

# LOGGING 설정
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} - {message}',
            'style': '{',
        },
        'detailed': {
            'format': '[{levelname}] {asctime} {name} {module} {pathname}:{lineno} - {message}',
            'style': '{',
        },
        'request': {
            'format': '[{levelname}] {asctime} {name} {module} - Request: {message}',
            'style': '{',
        },
        'response': {
            'format': '[{levelname}] {asctime} {name} {module} - Response: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'django.log',
            'formatter': 'detailed',
        },
        'request_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'request.log',
            'formatter': 'request',
        },
        'response_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'response.log',
            'formatter': 'response',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.response': {
            'handlers': ['response_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['file'],
            'level': 'DEBUG',
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