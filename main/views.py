from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # CSRF 테스트용 (실제로는 CSRF 처리 필요)
from django.conf import settings
import json
import logging
import os # os 모듈 임포트 추가

# 로거 설정
logger = logging.getLogger(__name__)

def index(request):
    # 환경 변수에서 API_KEY와 DEPLOYMENT_SHA를 가져옵니다.
    # 값이 없으면 기본값을 사용합니다 (개발 환경에서는 유용할 수 있음).
    api_key = os.environ.get('API_KEY', 'YOUR_DEFAULT_API_KEY') 
    deployment_sha = os.environ.get('DEPLOYMENT_SHA', 'localdev') # 캐시 버스팅에 사용될 수 있음
    
    context = {
        'api_key': api_key,
        'DEPLOYMENT_SHA': deployment_sha
    }
    return render(request, 'main/index.html', context)

@csrf_exempt # 실제 배포시에는 CSRF 보호를 올바르게 설정해야 합니다.
def frontend_debug_log(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            logger.info(f'[Frontend Log]: {message}') # print 대신 logger 사용
            return JsonResponse({'status': 'success', 'message': 'Log received'})
        except json.JSONDecodeError as e:
            logger.error(f'[Frontend Log Error] Invalid JSON: {e}')
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f'[Frontend Log Error] Exception: {e}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)
