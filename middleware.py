import logging
import time
import json
import traceback
import re
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

# 로거 설정
logger = logging.getLogger('security')
request_logger = logging.getLogger('django.request')
debug_logger = logging.getLogger('debug')

# 민감한 정보를 마스킹할 키워드 및 패턴
SENSITIVE_KEYS = (
    'password', 'token', 'key', 'secret', 'api_key', 'client_id', 'client_secret', 
    'access_token', 'refresh_token', 'auth', 'credential', 'jwt', 'session', 'cookie',
    'csrf', 'private', 'security', 'authentication'
)

# 민감한 정보를 마스킹하는 패턴
SENSITIVE_PATTERNS = [
    re.compile(r'(api[-_]?key|secret|token)["\']?\s*[=:]\s*["\']?([^"\'\s,}{]+)', re.IGNORECASE),
    re.compile(r'(access[-_]?token|refresh[-_]?token)["\']?\s*[=:]\s*["\']?([^"\'\s,}{]+)', re.IGNORECASE),
    re.compile(r'(password|pwd|passwd)["\']?\s*[=:]\s*["\']?([^"\'\s,}{]+)', re.IGNORECASE),
    re.compile(r'(Authorization|Bearer)[\s:]+([A-Za-z0-9-._~+/]+=*)', re.IGNORECASE),
    re.compile(r'(client[-_]?id|client[-_]?secret)["\']?\s*[=:]\s*["\']?([^"\'\s,}{]+)', re.IGNORECASE),
]

class RequestLoggingMiddleware:
    """
    HTTP 요청 및 응답 로깅 미들웨어
    
    오류 발생 시에만 상세 로깅을 하고, 일반 요청은 간결하게 처리합니다.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 요청 시작 시간
        start_time = time.time()
        request_id = f"{int(time.time())}_{id(request)}"
        
        # 간결한 요청 정보 로깅 (디버그 로깅은 하지 않음)
        if settings.DEBUG:
            logger.info(f"[{request_id}] {request.method} {request.path} 요청 시작")
        
        # 응답 처리
        try:
            response = self.get_response(request)
            
            # 응답 정보 로깅 (오류 응답에만 상세 로깅)
            duration = time.time() - start_time
            if response.status_code >= 500:
                self._log_error_response(request, response, duration, request_id)
            elif response.status_code >= 400:
                request_logger.warning(f"[{request_id}] {request.method} {request.path} - {response.status_code} - {duration:.2f}s")
            elif settings.DEBUG:
                logger.info(f"[{request_id}] {request.method} {request.path} - {response.status_code} - {duration:.2f}s")
            
            return response
        except Exception as e:
            # 예외 로깅 (항상 상세 로깅)
            self._log_exception(request, e, start_time, request_id)
            raise
    
    def _mask_sensitive_data(self, data):
        """민감한 정보 마스킹 함수"""
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                # 키가 민감한 정보인 경우 마스킹
                if isinstance(key, str) and any(sensitive_key in key.lower() for sensitive_key in SENSITIVE_KEYS):
                    masked_data[key] = '***MASKED***'
                # 재귀적으로 중첩된 딕셔너리 처리
                elif isinstance(value, (dict, list)):
                    masked_data[key] = self._mask_sensitive_data(value)
                else:
                    masked_data[key] = value
            return masked_data
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) if isinstance(item, (dict, list)) else item for item in data]
        elif isinstance(data, str):
            # 문자열에서 민감한 패턴 마스킹
            masked_str = data
            for pattern in SENSITIVE_PATTERNS:
                masked_str = pattern.sub(r'\1: ***MASKED***', masked_str)
            return masked_str
        else:
            return data
    
    def _log_error_response(self, request, response, duration, request_id):
        """오류 응답 정보를 상세하게 로깅"""
        error_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'request_id': request_id,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration': f"{duration:.4f}s",
            'remote_addr': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
        }
        
        # 응답 본문이 있다면 추가
        if hasattr(response, 'content'):
            try:
                if response.get('Content-Type', '').startswith('application/json'):
                    if len(response.content) < 1000:  # 응답이 너무 크지 않은 경우만
                        content_json = json.loads(response.content)
                        error_data['response_body'] = self._mask_sensitive_data(content_json)
            except Exception:
                pass
        
        request_logger.error(f"오류 응답: {json.dumps(error_data, ensure_ascii=False)}")
    
    def _log_exception(self, request, exception, start_time, request_id):
        """예외 정보를 로깅"""
        # 처리 시간 계산 
        duration = time.time() - start_time
        
        # 예외 정보
        exc_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'request_id': request_id,
            'method': request.method,
            'path': request.path,
            'exception': str(exception),
            'exception_type': type(exception).__name__,
            'duration': f"{duration:.4f}s",
            'remote_addr': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
        }
        
        # 트레이스백 추가
        exc_data['traceback'] = traceback.format_exc()
        
        # 요청 데이터 추가 (민감 정보 제외)
        if request.method in ('POST', 'PUT', 'PATCH') and hasattr(request, 'body'):
            try:
                if request.content_type == 'application/json':
                    body = json.loads(request.body)
                    # 민감 정보 마스킹
                    exc_data['request_body'] = self._mask_sensitive_data(body)
            except Exception:
                pass
        
        # 심각한 오류로 로깅
        request_logger.critical(f"예외 발생:\n{json.dumps(exc_data, ensure_ascii=False, indent=2)}")

class ApiKeyMiddleware:
    """
    API 키 인증을 처리하는 미들웨어
    
    특정 API 엔드포인트에 대해 X-Api-Key 헤더를 검증합니다.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # API 경로인 경우만 API 키 검증
        if request.path.startswith('/api/') and not request.path.startswith('/api/public/'):
            # API 키를 헤더에서 가져오기
            api_key = request.headers.get('X-Api-Key')
            
            # API 키가 없거나 일치하지 않는 경우
            if not api_key or api_key != settings.API_KEY:
                # 보안 로그 기록
                logger.warning(
                    f"API 키 인증 실패: IP={request.META.get('REMOTE_ADDR')}, "
                    f"Path={request.path}, Method={request.method}"
                )
                
                return JsonResponse({
                    'error': '인증에 실패했습니다. 유효한 API 키가 필요합니다.'
                }, status=403)
            
            # 인증 성공 로깅
            logger.info(
                f"API 키 인증 성공: IP={request.META.get('REMOTE_ADDR')}, "
                f"Path={request.path}, Method={request.method}"
            )
            
        # 다음 미들웨어로 요청 전달
        response = self.get_response(request)
        return response

class SecurityHeadersMiddleware:
    """
    보안 관련 HTTP 헤더를 추가하는 미들웨어
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # 보안 헤더 추가
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 배포 환경에서만 HSTS 헤더 추가
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # CSP(Content-Security-Policy) 헤더 추가
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",  # 필요한 외부 스크립트 소스 추가
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",  # 필요한 스타일 소스 추가
            "img-src 'self' data:",
            "font-src 'self' https://fonts.gstatic.com",
            "connect-src 'self'",
            "frame-src 'none'",
            "object-src 'none'",
        ]
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        return response 