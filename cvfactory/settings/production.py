"""
Production settings for cvfactory project.
배포 환경을 위한 설정을 포함합니다.
"""

from .base import *

# 환경변수에서 설정 가져오기
DEBUG = False
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Render 배포 설정
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# HTTPS 설정 (배포 환경용)
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 로그 설정 - 배포 환경 (INFO 레벨)
LOG_LEVEL = 'INFO'  # 로그 레벨을 INFO로 설정
LOG_TO_CONSOLE = True  # 콘솔 로깅 활성화
LOG_SQL_QUERIES = False  # SQL 쿼리 로깅 비활성화

# 로그 설정 - 배포 환경
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
        'ignore_render_healthcheck': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'Render' not in record.getMessage(),
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'application': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'application.log'),
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'api': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'api.log'),
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'errors.log'),
            'formatter': 'error_focused',
        },
        'security': {
            'level': 'INFO',
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
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'api', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console', 'application', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['errors', 'application'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['errors', 'api'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'api': {
            'handlers': ['console', 'api', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'groq_service': {
            'handlers': ['console', 'api', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'resume': {
            'handlers': ['console', 'application', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['console', 'security', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'crawlers': {
            'handlers': ['console', 'application', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        '': {  # 루트 로거
            'handlers': ['console', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.utils.autoreload': {
            'handlers': ['null'],
            'propagate': False,
        },
        'wsgi': {
            'handlers': ['null'],  # 콘솔에 출력하지 않음
            'level': 'WARNING',  # 경고 이상만 기록
            'propagate': False,
        },
    },
}

# 정적 파일 스토리지 설정 (폰트 로드 문제 해결)
STORAGES = {
    "default": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# 정적 파일 매니페스트 설정 변경
STATICFILES_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'static')

# 중복 로그 방지를 위한 propagate 설정 (모든 로거에 propagate=False 설정)
for logger_name in LOGGING['loggers']:
    LOGGING['loggers'][logger_name]['propagate'] = False 