#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging
import traceback
from datetime import datetime
import glob

# logs 디렉토리 생성
os.makedirs('logs', exist_ok=True)

# 기본 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] - %(funcName)s() - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join('logs', 'startup.log'), mode='a')
    ]
)

# 루트 로거 가져오기
logger = logging.getLogger()


def clear_log_files():
    """서버 시작 시 로그 파일들을 초기화합니다."""
    try:
        log_files = glob.glob(os.path.join('logs', '*.log'))
        for log_file in log_files:
            with open(log_file, 'w') as f:
                # 파일 내용을 비우고 닫기
                pass
        logger.info(f"{len(log_files)}개의 로그 파일을 초기화했습니다.")
    except Exception as e:
        logger.error(f"로그 파일 초기화 중 오류 발생: {e}")


def main():
    """Run administrative tasks."""
    start_time = datetime.now()
    logger.info("="*80)
    logger.info(f"서버 시작 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"실행 경로: {os.getcwd()}")
    logger.info(f"Python 버전: {sys.version}")
    logger.info(f"명령 인자: {sys.argv}")
    
    # 환경 변수 디버깅
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'env_configs', '.env'))
        env_vars = {key: value for key, value in os.environ.items() 
                   if not key.startswith('PATH') and not key.startswith('PYTHONPATH')}
        logger.debug(f"환경 변수: {env_vars}")
    except Exception as e:
        logger.error(f"환경 변수 로드 중 오류: {e}")
    
    # Django 설정 모듈 로드
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cvfactory.settings")
    logger.info(f"설정 모듈: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
    try:
        from django.core.management import execute_from_command_line
        logger.info("Django 관리 모듈 로드 성공")
        
        # 패키지 버전 정보 기록
        try:
            import django
            import rest_framework
            logger.info(f"Django 버전: {django.get_version()}")
            logger.info(f"DRF 버전: {rest_framework.VERSION}")
        except Exception as e:
            logger.warning(f"패키지 버전 확인 중 오류: {e}")
        
        # 명령 실행
        logger.info(f"명령 실행: {' '.join(sys.argv)}")
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        error_msg = (
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
        logger.error(error_msg)
        logger.error(f"ImportError: {exc}")
        logger.error(f"스택 트레이스: {traceback.format_exc()}")
        raise ImportError(error_msg) from exc
    except Exception as e:
        logger.critical(f"예상치 못한 오류 발생: {e}")
        logger.critical(f"스택 트레이스: {traceback.format_exc()}")
        raise
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"실행 시간: {duration.total_seconds():.2f}초")
        logger.info("="*80)


if __name__ == "__main__":
    try:
        # 서버 실행 시 항상 로그 파일 초기화
        clear_log_files()
            
        main()
    except KeyboardInterrupt:
        logger.info("사용자에 의해 프로그램 종료")
    except Exception as e:
        logger.critical(f"치명적 오류: {e}")
        logger.critical(f"상세 오류: {traceback.format_exc()}")
        sys.exit(1)
