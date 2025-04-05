import logging
from django.http import JsonResponse
from django.conf import settings

# 로거 설정
logger = logging.getLogger('security')

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