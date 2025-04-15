import os
import shutil
import logging

logger = logging.getLogger('crawlers')

def clear_crawling_logs():
    """서버 시작 시 크롤링 로그 디렉토리를 초기화합니다."""
    log_dir = os.path.join("logs", "crawling")
    
    if os.path.exists(log_dir):
        try:
            # 디렉토리 내 모든 파일 삭제
            for file in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            logger.info("크롤링 로그 디렉토리가 초기화되었습니다.")
        except Exception as e:
            logger.error(f"크롤링 로그 디렉토리 초기화 중 오류 발생: {str(e)}")
    else:
        # 디렉토리가 없으면 생성
        os.makedirs(log_dir, exist_ok=True)
        logger.info("크롤링 로그 디렉토리가 생성되었습니다.")
