import os
import glob
import logging
from django.core.management.commands.runserver import Command as RunserverCommand

logger = logging.getLogger('cvfactory')

class Command(RunserverCommand):
    """
    로그 파일을 초기화한 후 Django 서버를 실행하는 커스텀 명령어
    사용법: python manage.py runserver_clear
    """
    
    def handle(self, *args, **options):
        """
        서버 시작 전에 로그 파일을 초기화하고 runserver 원본 기능 실행
        """
        # 로그 초기화 진행
        self.clear_log_files()
        
        # 원본 runserver 명령 실행
        super().handle(*args, **options)
    
    def clear_log_files(self):
        """서버 시작 시 로그 파일들을 초기화합니다."""
        try:
            # 로그 디렉토리가 없으면 생성
            os.makedirs('logs', exist_ok=True)
            
            # 1. 코어 로그 파일 목록 (유지하고 초기화할 파일들)
            core_log_files = [
                os.path.join('logs', 'app.log'),
                os.path.join('logs', 'api.log'),
                os.path.join('logs', 'error.log'),
                os.path.join('logs', 'startup.log')
            ]
            
            # 2. 이전 로그 파일들 (삭제할 파일들)
            legacy_log_files = [
                os.path.join('logs', 'django.log'),
                os.path.join('logs', 'debug.log'),
                os.path.join('logs', 'resume.log'),
                os.path.join('logs', 'security.log'),
                os.path.join('logs', 'advanced_debug.log'),
                os.path.join('logs', 'sql.log'),
                os.path.join('logs', 'request.log'),
                os.path.join('logs', 'django_db.log'),
                os.path.join('logs', 'django_request.log'), 
                os.path.join('logs', 'django_response.log'),
                os.path.join('logs', 'performance.log'),
                os.path.join('logs', 'wsgi.log'),
                os.path.join('logs', 'groq.log'),
                os.path.join('logs', 'groq_service_debug.log'),
            ]
            
            # 3. 코어 로그 파일 초기화 (내용만 비움)
            for log_file in core_log_files:
                try:
                    with open(log_file, 'w') as f:
                        # 파일 내용을 비우고 닫기
                        pass
                    logger.info(f"코어 로그 파일 초기화: {log_file}")
                except Exception as e:
                    logger.error(f"로그 파일 초기화 중 오류: {log_file} - {e}")
            
            # 4. 이전(레거시) 로그 파일 삭제
            removed_count = 0
            for log_file in legacy_log_files:
                if os.path.exists(log_file):
                    try:
                        os.remove(log_file)
                        removed_count += 1
                        logger.info(f"불필요한 로그 파일 삭제: {log_file}")
                    except Exception as e:
                        logger.error(f"로그 파일 삭제 중 오류: {log_file} - {e}")
            
            # 5. 추가적으로 발견된 로그 파일 삭제 (이름 패턴으로 필요없는 로그 파일 찾기)
            core_filenames = [os.path.basename(f) for f in core_log_files]
            extra_log_files = glob.glob(os.path.join('logs', '*.log'))
            
            extra_removed = 0
            for log_file in extra_log_files:
                if os.path.basename(log_file) not in core_filenames:
                    try:
                        os.remove(log_file)
                        extra_removed += 1
                        logger.info(f"추가 발견된 불필요 로그 파일 삭제: {log_file}")
                    except Exception as e:
                        logger.error(f"추가 로그 파일 삭제 중 오류: {log_file} - {e}")
            
            logger.info(f"로그 파일 정리 요약: {len(core_log_files)}개 코어 로그 파일 초기화, {removed_count + extra_removed}개 불필요 파일 삭제")
            
            # 6. 크롤링 로그 디렉토리 정리
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