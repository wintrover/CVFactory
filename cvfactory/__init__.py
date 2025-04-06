import os
import logging

# 로그 디렉토리 생성
os.makedirs('logs', exist_ok=True)

# 기본 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

# 초기 로깅
logger = logging.getLogger(__name__)
logger.debug("Django 애플리케이션 초기화 중...")
