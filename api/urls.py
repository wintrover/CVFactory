from django.urls import path
from .views import create_resume, fetch_company_info, test_groq_logging
  # views.py에서 함수 가져오기

urlpatterns = [
    path("create_resume/", create_resume, name="create_resume"),  
    path("fetch_company_info/", fetch_company_info, name="fetch_company_info"),  # ✅ 회사 정보 크롤링 API 추가
    path('test_groq_logging/', test_groq_logging, name='test_groq_logging'),
]
