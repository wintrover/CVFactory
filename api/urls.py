from django.urls import path, include
from .views import create_resume, fetch_company_info, test_groq_logging
  # views.py에서 함수 가져오기
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db import connection

@api_view(['GET'])
def health_check(request):
    """
    헬스 체크 엔드포인트 - Render 배포를 위한 상태 확인
    데이터베이스 연결 테스트를 포함합니다.
    """
    try:
        # 데이터베이스 연결 테스트
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            one = cursor.fetchone()[0]
            if one != 1:
                raise Exception("데이터베이스 쿼리 실패")
        
        return Response(
            {"status": "healthy", "database": "connected"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"status": "unhealthy", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

urlpatterns = [
    # 헬스 체크 엔드포인트
    path('health/', health_check, name='health_check'),
    
    # 공개 API 경로 - 인증이 필요 없음
    path("public/", include("api.public.urls")),
    
    # 인증이 필요한 API 경로
    path("create_resume/", create_resume, name="create_resume"),  
    path("fetch_company_info/", fetch_company_info, name="fetch_company_info"),  # ✅ 회사 정보 크롤링 API 추가
    path('test_groq_logging/', test_groq_logging, name='test_groq_logging'),
]
