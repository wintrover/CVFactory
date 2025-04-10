"""
Django settings for cvfactory project.
"""

from pathlib import Path
import logging.config
import os
from dotenv import load_dotenv
from datetime import timedelta 
import dj_database_url  # 데이터베이스 URL 지원을 위한 패키지 추가

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 환경변수 로드
load_dotenv()

# API 키 설정
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    # 개발 환경에서만 경고 로그와 임시 키 생성
    import logging
    import uuid
    logger = logging.getLogger('app')
    logger.warning("API_KEY가 설정되지 않았습니다. 임시 키를 생성합니다. 프로덕션 환경에서는 반드시 API_KEY를 설정하세요.")
    API_KEY = f"dev-key-{uuid.uuid4().hex[:8]}"  # 개발용 임시 키 생성

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
    "django_extensions",  # HTTPS 개발 서버 지원
    "cvfactory",  # 프로젝트 앱 - 사용자 정의 명령어 로드
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
CSRF_COOKIE_HTTPONLY = False  # JavaScript에서 CSRF 토큰에 접근할 수 있도록 설정
CSRF_COOKIE_SAMESITE = 'None'  # SameSite 정책을 None으로 설정
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

# 보안 헤더 설정
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

MIDDLEWARE = [
    "middleware.RequestLoggingMiddleware",  # 요청 로깅 미들웨어 (최상단에 배치)
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # WhiteNoise 정적 파일 제공 미들웨어
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "allauth.account.middleware.AccountMiddleware",  # allauth 미들웨어 주석 처리 (버전 호환성 문제)
    # "middleware.ApiKeyMiddleware",  # API 키 인증 미들웨어 - 비활성화
    "middleware.SecurityHeadersMiddleware",  # 보안 헤더 미들웨어
    "middleware.JWTUserStatusMiddleware",  # JWT 사용자 상태 확인 미들웨어 (CVE-2024-22513 완화)
    "middleware.RateLimitMiddleware",  # API 요청 속도 제한 미들웨어
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
    BASE_DIR / "static_dev",
    BASE_DIR / "frontend",
]
STATIC_ROOT = BASE_DIR / "static_prod"

# WhiteNoise 설정 - 배포 환경에서 정적 파일 제공 최적화
STORAGES = {
    "default": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

WSGI_APPLICATION = "cvfactory.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///" + str(BASE_DIR / "db.sqlite3"),
        conn_max_age=600
    )
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',  
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),  # 1일에서 1시간으로 단축
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # 7일에서 1일로 단축
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "UPDATE_LAST_LOGIN": True,  # 마지막 로그인 시간 업데이트
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv('DJANGO_SECRET_KEY'),
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    # 토큰에 클레임 추가
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    # 클레임 검증 추가
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
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