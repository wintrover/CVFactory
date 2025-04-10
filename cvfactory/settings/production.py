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
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'django.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'api_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'api.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'resume_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'resume.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'security_file': {
            'level': 'INFO',
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
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'debug.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
            'filters': ['ignore_render_healthcheck'],
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security_file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'api': {
            'handlers': ['console', 'api_file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'groq_service': {
            'handlers': ['console', 'api_file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'resume': {
            'handlers': ['console', 'resume_file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['console', 'security_file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'crawlers': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        '': {  # 루트 로거
            'handlers': ['console', 'error_file'],
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