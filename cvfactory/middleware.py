import logging
import json
import time
from django.utils.timezone import now

logger = logging.getLogger('django')
request_logger = logging.getLogger('django.request')
response_logger = logging.getLogger('django.response')

class RequestLoggingMiddleware:
    """
    모든 HTTP 요청과 응답을 자동으로 로깅하는 미들웨어
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 요청 시작 시간 기록
        start_time = time.time()
        
        # 요청 정보 로깅
        request_body = None
        content_type = request.headers.get('Content-Type', '')
        
        if request.body and 'application/json' in content_type:
            try:
                request_body = json.loads(request.body)
            except:
                request_body = str(request.body)
        elif request.body:
            request_body = str(request.body)
            
        request_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') else 'AnonymousUser',
            'ip': request.META.get('REMOTE_ADDR'),
            'headers': dict(request.headers),
            'body': request_body,
            'GET': dict(request.GET),
            'POST': dict(request.POST),
            'time': now().isoformat()
        }
        
        request_logger.info(f"요청: {json.dumps(request_data, ensure_ascii=False, default=str)}")
        
        # 응답 처리
        response = self.get_response(request)
        
        # 소요 시간 계산
        duration = time.time() - start_time
        
        # 응답 정보 로깅
        content = None
        if hasattr(response, 'content'):
            try:
                if 'application/json' in response.get('Content-Type', ''):
                    content = json.loads(response.content)
                else:
                    content = str(response.content)[:1000] + '...' if len(str(response.content)) > 1000 else str(response.content)
            except:
                content = "로깅 불가능한 컨텐츠"
        
        response_data = {
            'status_code': response.status_code,
            'content': content,
            'headers': dict(response.headers),
            'duration': f"{duration:.4f}초",
            'time': now().isoformat()
        }
        
        response_logger.info(f"응답: {json.dumps(response_data, ensure_ascii=False, default=str)}")
        
        # 일반 로그에도 요약 정보 기록
        logger.info(
            f"[{request.method}] {request.path} - {response.status_code} ({duration:.4f}초)"
        )
        
        return response 