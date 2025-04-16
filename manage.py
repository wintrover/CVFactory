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
        # 로그 디렉토리가 없으면 생성
        os.makedirs('logs', exist_ok=True)
        
        # 1. 유지할 코어 로그 파일 목록
        core_logs = [
            os.path.join('logs', 'app.log'),
            os.path.join('logs', 'api.log'),
            os.path.join('logs', 'error.log'),
            os.path.join('logs', 'startup.log')
        ]
        
        # 2. 현재 로그 파일 목록 확인
        current_logs = glob.glob(os.path.join('logs', '*.log'))
        logger.info(f"현재 로그 파일 {len(current_logs)}개 발견")
        
        # 3. 불필요한 로그 파일 삭제
        core_filenames = [os.path.basename(f) for f in core_logs]
        removed_count = 0
        
        for log_file in current_logs:
            base_name = os.path.basename(log_file)
            if base_name not in core_filenames:
                try:
                    # 백업 없이 바로 삭제
                    os.remove(log_file)
                    removed_count += 1
                    logger.info(f"불필요한 로그 파일 삭제: {base_name}")
                except Exception as e:
                    logger.error(f"로그 파일 삭제 중 오류: {base_name} - {e}")
        
        # 4. 코어 로그 파일 초기화
        for log_file in core_logs:
            try:
                # 파일 내용을 비움
                with open(log_file, 'w', encoding='utf-8') as f:
                    pass
                logger.info(f"로그 파일 초기화: {os.path.basename(log_file)}")
            except Exception as e:
                logger.error(f"로그 파일 초기화 중 오류: {log_file} - {e}")
        
        logger.info(f"{len(core_logs)}개의 로그 파일을 초기화했습니다.")
        
        # 5. 크롤링 로그 디렉토리 초기화
        crawling_log_dir = os.path.join('logs', 'crawling')
        if os.path.exists(crawling_log_dir):
            crawling_logs = glob.glob(os.path.join(crawling_log_dir, '*.txt'))
            for log_file in crawling_logs:
                try:
                    os.remove(log_file)
                except Exception as e:
                    logger.error(f"크롤링 로그 파일 삭제 중 오류: {log_file} - {e}")
            logger.info(f"{len(crawling_logs)}개의 크롤링 로그 파일을 초기화했습니다.")
        else:
            os.makedirs(crawling_log_dir, exist_ok=True)
            logger.info("크롤링 로그 디렉토리를 생성했습니다.")
            
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
