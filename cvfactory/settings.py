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
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드
load_dotenv(dotenv_path=BASE_DIR / "env_configs" / ".env.development")

# 환경변수 로드
load_dotenv()

# 환경변수에서 설정 가져오기
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'  # 기본값은 보안을 위해 False로 설정
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# API 키 설정
API_KEY = os.getenv('API_KEY')
if not API_KEY and DEBUG:
    # 개발 환경에서만 경고 로그와 임시 키 생성
    import logging
    import uuid
    logger = logging.getLogger('app')
    logger.warning("API_KEY가 설정되지 않았습니다. 임시 키를 생성합니다. 프로덕션 환경에서는 반드시 API_KEY를 설정하세요.")
    API_KEY = f"dev-key-{uuid.uuid4().hex[:8]}"  # 개발용 임시 키 생성
elif not API_KEY and not DEBUG:
    # 프로덕션 환경에서 키가 없으면 경고
    import logging
    logger = logging.getLogger('app')
    logger.error("프로덕션 환경에서 API_KEY가 설정되지 않았습니다. API 기능이 작동하지 않을 수 있습니다.")

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
    "django.contrib.sitemaps",

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
    "django_seo_js",
]

# CORS 설정
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,https://cvfactory.kr').split(',')
CORS_ALLOW_CREDENTIALS = True

# Cloudflare 관련 CORS 추가 설정
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cf-connecting-ip',  # Cloudflare IP 헤더
    'cf-ipcountry',      # Cloudflare 국가 헤더
]

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
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,https://cvfactory.kr,https://*.cvfactory.kr').split(',')

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

# 기본 미들웨어 설정
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",  # 캐시 미들웨어를 상단에 배치
    'django_seo_js.middleware.UserAgentMiddleware',
    "middleware.RequestLoggingMiddleware",  # 요청 로깅 미들웨어
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
    "middleware.CloudflareMiddleware",  # Cloudflare CDN 최적화 미들웨어
    "django.middleware.cache.FetchFromCacheMiddleware",  # 페어로 하단에 배치
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

# 프로덕션 환경에서 템플릿 캐싱 활성화
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# 정적 파일 설정
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static_dev",
    BASE_DIR / "frontend",
    BASE_DIR / "static",
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

# 정적 파일 매니페스트 엄격 모드 비활성화
STATICFILES_MANIFEST_STRICT = False

# WhiteNoise 최적화 설정
WHITENOISE_MAX_AGE = 604800  # 1주일 (초 단위)
WHITENOISE_COMPRESSION_QUALITY = 90
WHITENOISE_IMMUTABLE_FILE_TEST = lambda path, url: True if url.endswith('.css') or url.endswith('.js') else False
WHITENOISE_AUTOREFRESH = False if not DEBUG else True

# 이미지 최적화 설정
STATIC_IMAGE_COMPRESS = True

# 브라우저 캐싱을 위한 HTTP 캐시 설정
if DEBUG:
    # 개발 환경에서도 캐싱 적용 (더 짧은 시간)
    CACHE_MIDDLEWARE_SECONDS = 10  # 10초
    # 캐시 설정
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake-dev',
            'TIMEOUT': 10,  # 10초
        }
    }
else:
    # 프로덕션 환경 캐싱 설정 (Cloudflare 최적화)
    CACHE_MIDDLEWARE_SECONDS = 86400  # 24시간
    # 캐시 설정
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': 86400,  # 24시간
            'OPTIONS': {
                'MAX_ENTRIES': 5000,  # 캐시 항목 최대 개수
                'CULL_FREQUENCY': 3,  # 캐시 항목이 최대치에 도달했을 때 제거할 항목 비율 (1/3)
            }
        },
        'cloudflare': {  # Cloudflare 전용 캐시
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'cloudflare-cache',
            'TIMEOUT': 604800,  # 1주일
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            }
        }
    }
    
    # 응답 헤더에 캐시 제어 설정 추가
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_KEY_PREFIX = 'cvfactory'
    
    # HTML 응답에 대한 캐시 제어 설정
    HTML_CACHE_TTL = 3600  # 1시간

WSGI_APPLICATION = "cvfactory.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///" + str(BASE_DIR / "db.sqlite3"),
        conn_max_age=600,
        options={
            'timeout': 20,
            'connect_timeout': 10,
        }
    )
}

# CDN 설정 (프로덕션 환경)
if not DEBUG:
    # Cloudflare CDN 설정 활성화
    STATIC_URL = 'https://cvfactory.kr/static/'
    
    # Cloudflare 관련 보안 설정
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
    
    # Cloudflare 캐시 최적화
    WHITENOISE_MAX_AGE = 31536000  # 1년 (초 단위)

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
    "SIGNING_KEY": SECRET_KEY,
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

# 환경변수에서 로그 레벨 가져오기
LOG_LEVEL = 'DEBUG'  # 로그 레벨을 INFO에서 DEBUG로 변경
LOG_TO_CONSOLE = True  # 콘솔 로깅 활성화
LOG_SQL_QUERIES = True  # SQL 쿼리 로깅 활성화

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
        'error_focused': {
            'format': '\n******** ERROR ********\n[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s]\n%(message)s\n%(exc_info)s\n************************',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'debug_detailed': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] [%(funcName)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'advanced_debug': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] [%(funcName)s] [%(process)d:%(thread)d] - %(message)s\n%(exc_info)s',
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
        'ignore_render_healthcheck': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'Render' not in record.getMessage(),
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'debug_detailed',
            'filters': ['ignore_render_healthcheck'],
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'django.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'api_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'api.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'resume_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'resume.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'security_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'security.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'error.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'error_focused',
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'debug.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'debug_detailed',
            'filters': ['ignore_render_healthcheck'],
        },
        'advanced_debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'advanced_debug.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'advanced_debug',
            'filters': ['ignore_render_healthcheck'],
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'sql_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'sql.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'debug_detailed',
        },
        'startup_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'startup.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'debug_detailed',
        },
        'request_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'request.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'advanced_debug',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file', 'error_file', 'debug_file', 'request_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console', 'file', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['error_file', 'sql_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security_file', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'api': {
            'handlers': ['console', 'api_file', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'groq_service': {
            'handlers': ['console', 'api_file', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'resume': {
            'handlers': ['console', 'resume_file', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'security': {
            'handlers': ['console', 'security_file', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'crawlers': {
            'handlers': ['console', 'file', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        '': {  # 루트 로거
            'handlers': ['console', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.utils.autoreload': {
            'handlers': ['null'],
            'propagate': False,
        },
        'cvfactory': {
            'handlers': ['console', 'file', 'error_file', 'debug_file', 'startup_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'middleware': {
            'handlers': ['console', 'file', 'error_file', 'debug_file', 'advanced_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
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

# SEO JS 설정 
SEO_JS_ENABLED = True
SEO_JS_BACKEND = "django_seo_js.backends.PrerenderIO"  # 또는 자체 구현 백엔드 사용
SEO_JS_PRERENDER_TOKEN = "your-prerender-token"  # 실제 토큰으로 변경 필요
SEO_JS_PRERENDER_URL = "https://service.prerender.io/"
SEO_JS_PRERENDER_RECACHE_URL = "https://api.prerender.io/recache"

# SEO JS 예외 URL 패턴
SEO_JS_EXCLUDES = [
    r'/admin/',
    r'/api/',
    r'/static/',
]