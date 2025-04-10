"""
환경에 따라 적절한 설정 모듈을 가져옵니다.
DJANGO_SETTINGS_MODULE 환경 변수나 RENDER 환경 변수를 사용하여 결정합니다.
"""

import os

# 기본 설정은 개발 환경
# 배포 환경인 경우 Render 환경 변수를 확인하여 production 설정 사용
if os.environ.get('RENDER') or os.environ.get('DJANGO_SETTINGS_MODULE') == 'cvfactory.settings.production':
    from .production import *
else:
    from .development import *

print(f"Settings loaded: {'Production' if os.environ.get('RENDER') else 'Development'} (DEBUG={DEBUG})") 