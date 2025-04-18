"""
Development settings for cvfactory project.
디버그 모드와 로컬 개발을 위한 설정을 포함합니다.
"""

from .base import *

# .env 파일 로드 (개발 환경)
load_dotenv(dotenv_path=BASE_DIR / "env_configs" / ".env.development")

# 환경변수에서 설정 가져오기
DEBUG = True
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-development-secret-key')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# HTTPS 설정 (개발 환경에서는 비활성화)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# 로그 설정 - 개발 환경 (DEBUG 레벨)
LOG_LEVEL = 'DEBUG'  # 로그 레벨을 DEBUG로 설정
LOG_TO_CONSOLE = True  # 콘솔 로깅 활성화
LOG_SQL_QUERIES = True  # SQL 쿼리 로깅 활성화

# 로그 설정 - 개발 환경
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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'application': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'application.log'),
            'formatter': 'verbose',
        },
        'api': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'api.log'),
            'formatter': 'verbose',
        },
        'errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'errors.log'),
            'formatter': 'error_focused',
        },
        'security': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'security.log'),
            'formatter': 'verbose',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'application', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'api', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console', 'application', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['errors', 'application'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['errors', 'api'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'api': {
            'handlers': ['console', 'api', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'groq_service': {
            'handlers': ['console', 'api', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'resume': {
            'handlers': ['console', 'application', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'security': {
            'handlers': ['console', 'security', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'crawlers': {
            'handlers': ['console', 'application', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        '': {  # 루트 로거
            'handlers': ['console', 'errors'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.utils.autoreload': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
} 