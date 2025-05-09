from django.urls import path
from . import views

app_name = 'main' # URL 네임스페이스 설정

urlpatterns = [
    path('', views.index, name='index'),
    path('frontend-debug-log/', views.frontend_debug_log, name='frontend_debug_log'),
    path('health/', views.health_check, name='health_check'),
] 