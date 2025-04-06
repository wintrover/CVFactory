from django.urls import path
from . import views

urlpatterns = [
    # 인증 관련 API
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    
    # 시스템 상태 API
    path('status/', views.api_status, name='api_status'),
] 