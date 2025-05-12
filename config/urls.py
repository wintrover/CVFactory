"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from core import views # core.views 모듈을 임포트합니다.
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path('' , views.index, name='index'), # 루트 URL('')에 core.views.index 뷰를 연결합니다.
]

# 개발 환경에서만 정적 파일을 제공합니다.
# if settings.DEBUG:
#     urlpatterns += staticfiles_urlpatterns() # 이 줄은 삭제됩니다.
