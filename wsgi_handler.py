#!/usr/bin/env python
import os
import sys
import logging

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Django 설정 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cvfactory.settings')

# Django의 WSGI 애플리케이션 가져오기
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    logger.info("WSGI 애플리케이션 로드 성공")
except Exception as e:
    logger.error(f"WSGI 애플리케이션 로드 실패: {e}")
    raise e

# AWS Lambda 핸들러 정의 (serverless-wsgi 플러그인이 사용)
def handler(event, context):
    logger.info("Lambda 요청 처리")
    
    # 인증 헤더 없는 경우를 위한 임시 처리
    # 이 부분은 환경변수를 통해 제어 가능
    if os.environ.get('STAGE') == 'dev':
        if 'headers' in event and 'x-api-key' not in event['headers']:
            # 개발 환경에서는 API 키 자동 추가
            if 'headers' not in event:
                event['headers'] = {}
            event['headers']['x-api-key'] = os.environ.get('API_KEY', 'default-dev-api-key-change-in-production')
    
    # 요청 내용 로깅 (민감 정보 제외)
    if 'requestContext' in event and 'path' in event['requestContext']:
        path = event['requestContext'].get('path', '')
        method = event['requestContext'].get('http', {}).get('method', '')
        if path and method:
            logger.info(f"요청: {method} {path}")
    
    try:
        # serverless-wsgi에서 제공하는 핸들러 가져오기
        from serverless_wsgi import handle_request
        return handle_request(application, event, context)
    except Exception as e:
        logger.error(f"요청 처리 중 오류 발생: {e}")
        # Lambda 오류 응답 반환
        return {
            'statusCode': 500,
            'body': '서버 오류가 발생했습니다.',
            'headers': {
                'Content-Type': 'text/plain'
            }
        } 