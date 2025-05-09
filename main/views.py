from django.shortcuts import render
from django.http import JsonResponse, HttpResponse # HttpResponse 추가
from django.views.decorators.csrf import csrf_exempt # CSRF 테스트용 (실제로는 CSRF 처리 필요)
from django.conf import settings
import json
import logging
import os # os 모듈 임포트 추가

# 로거 설정
logger = logging.getLogger(__name__)

def index(request):
    try:
        context = {
            'api_key': settings.API_KEY,
            'deployment_sha': settings.DEPLOYMENT_SHA
        }
        return render(request, 'main/index.html', context)
    except Exception as e:
        logger.error(f"Error rendering index page: {e}", exc_info=True)
        # 사용자에게 보여줄 적절한 오류 페이지나 메시지를 반환할 수 있습니다.
        # 여기서는 간단히 500 오류를 발생시키거나, 기본 오류 템플릿을 렌더링할 수 있습니다.
        # raise # 또는 HttpResponseServerError("An error occurred.")
        return render(request, 'main/500.html', {"error_message": str(e)}, status=500)

@csrf_exempt # 실제 배포시에는 CSRF 보호를 올바르게 설정해야 합니다.
def frontend_debug_log(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            level = data.get('level', 'INFO').upper()

            log_message = f"[FRONTEND-{level}] {message}"

            if level == 'ERROR':
                logger.error(log_message)
            elif level == 'WARNING':
                logger.warning(log_message)
            elif level == 'DEBUG':
                logger.debug(log_message)
            else:
                logger.info(log_message)
            
            return JsonResponse({'status': 'success', 'message': 'Log received'})
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from frontend log: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logger.error(f"Error processing frontend log: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def health_check(request):
    return HttpResponse("OK", status=200)
