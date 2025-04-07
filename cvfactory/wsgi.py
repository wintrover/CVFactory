"""
WSGI config for cvfactory project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
import logging
import traceback
from datetime import datetime
import time

# 로깅 설정
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'wsgi.log'), 'a')
    ]
)
logger = logging.getLogger('wsgi')

logger.info("="*80)
logger.info(f"WSGI 애플리케이션 초기화 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"실행 경로: {os.getcwd()}")
logger.info(f"Python 버전: {sys.version}")

try:
    # 환경 변수 디버깅
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'env_configs', '.env'))
    env_vars = {key: value for key, value in os.environ.items() 
               if not key.startswith('PATH') and not key.startswith('PYTHONPATH')}
    logger.debug(f"환경 변수: {env_vars}")
except Exception as e:
    logger.error(f"환경 변수 로드 중 오류: {e}")

# Django 설정 모듈 로드
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cvfactory.settings")
logger.info(f"설정 모듈: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    logger.info("Django WSGI 애플리케이션 로드 시작")
    start_time = time.time()
    from django.core.wsgi import get_wsgi_application
    _application = get_wsgi_application()
    load_time = time.time() - start_time
    logger.info(f"Django WSGI 애플리케이션 로드 완료 (소요 시간: {load_time:.2f}초)")
    
    # 버전 정보
    try:
        import django
        logger.info(f"Django 버전: {django.get_version()}")
    except Exception as e:
        logger.warning(f"Django 버전 확인 중 오류: {e}")

    # WSGI 미들웨어 래퍼 - 간소화된 버전
    def application(environ, start_response):
        """WSGI 애플리케이션 래퍼 - 응답 로깅"""
        request_time = datetime.now()
        path_info = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')
        query_string = environ.get('QUERY_STRING', '')
        remote_addr = environ.get('REMOTE_ADDR', '')
        
        request_id = f"{int(time.time())}_{id(environ)}"
        logger.debug(f"요청 시작 [{request_id}] - {method} {path_info}?{query_string} ({remote_addr})")
        
        try:
            start_process = time.time()
            # 원본 애플리케이션 호출
            response = _application(environ, start_response)
            process_time = time.time() - start_process
            
            # 요청 완료 로깅
            response_time = datetime.now()
            duration = (response_time - request_time).total_seconds()
            logger.debug(f"요청 완료 [{request_id}] - 처리 시간: {process_time:.4f}초, 총 시간: {duration:.4f}초")
            
            # 원본 응답 반환 (수정 없이)
            return response
            
        except Exception as e:
            logger.error(f"요청 처리 중 오류 [{request_id}]: {e}")
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            raise
            
except Exception as e:
    logger.critical(f"WSGI 애플리케이션 초기화 중 오류: {e}")
    logger.critical(f"스택 트레이스: {traceback.format_exc()}")
    # 기본 WSGI 애플리케이션을 생성하여 오류 보고
    def application(environ, start_response):
        status = '500 Internal Server Error'
        error_message = f'WSGI 애플리케이션 초기화 중 오류가 발생했습니다: {str(e)}'
        output = error_message.encode()
        response_headers = [('Content-type', 'text/plain'),
                           ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]

logger.info(f"WSGI 애플리케이션 초기화 완료 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("="*80)
