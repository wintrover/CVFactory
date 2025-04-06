from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.middleware.csrf import get_token
import logging
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# 로거 설정
logger = logging.getLogger('api')

# CSRF 토큰 제공 API
@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    CSRF 토큰을 쿠키로 설정하고 반환하는 API 엔드포인트
    
    클라이언트가 CSRF 보호된 API를 호출하기 전에 이 엔드포인트를 호출해야 함
    """
    token = get_token(request)
    return JsonResponse({"csrfToken": token})

# 로그인 API
@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_protect
def user_login(request):
    """
    사용자 로그인 API 엔드포인트
    
    username과 password를 받아 인증하고 토큰을 발급
    """
    try:
        data = json.loads(request.body)
        username = data.get("username", "")
        password = data.get("password", "")
        
        if not username or not password:
            return JsonResponse({
                "error": "사용자 이름과 비밀번호를 모두 입력해주세요."
            }, status=400)
        
        # 사용자 인증
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # 세션 기반 로그인
            login(request, user)
            
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # 사용자 정보
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
            }
            
            # 로그인 성공 응답
            return JsonResponse({
                "message": "로그인 성공",
                "user": user_data,
                "access": access_token,
                "refresh": str(refresh),
            })
        else:
            # 로그인 실패
            return JsonResponse({
                "error": "사용자 이름 또는 비밀번호가 올바르지 않습니다."
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "올바른 JSON 형식이 아닙니다."
        }, status=400)
    except Exception as e:
        logger.error(f"로그인 처리 중 오류: {str(e)}", exc_info=True)
        return JsonResponse({
            "error": "서버 오류가 발생했습니다."
        }, status=500)

# 회원가입 API
@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_protect
def user_register(request):
    """
    사용자 회원가입 API 엔드포인트
    
    username, email, password를 받아 새 사용자 계정 생성
    """
    try:
        data = json.loads(request.body)
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        # 필수 필드 확인
        if not username or not email or not password:
            return JsonResponse({
                "error": "사용자 이름, 이메일, 비밀번호를 모두 입력해주세요."
            }, status=400)
        
        # 사용자 이름 중복 확인
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "error": "이미 사용 중인 사용자 이름입니다."
            }, status=400)
        
        # 이메일 중복 확인
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "error": "이미 사용 중인 이메일입니다."
            }, status=400)
        
        # 새 사용자 생성
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # 회원가입 완료 후 자동 로그인
        login(request, user)
        
        # 회원가입 및 로그인 성공 응답
        return JsonResponse({
            "message": "회원가입 및 로그인 성공",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "access": access_token,
            "refresh": str(refresh),
        })
            
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "올바른 JSON 형식이 아닙니다."
        }, status=400)
    except Exception as e:
        logger.error(f"회원가입 처리 중 오류: {str(e)}", exc_info=True)
        return JsonResponse({
            "error": "서버 오류가 발생했습니다."
        }, status=500)

# 로그아웃 API
@api_view(["POST"])
@csrf_protect
def user_logout(request):
    """
    사용자 로그아웃 API 엔드포인트
    
    세션을 종료하고 로그아웃 처리
    """
    try:
        # 세션 기반 로그아웃
        logout(request)
        
        # 로그아웃 성공 응답
        return JsonResponse({
            "message": "로그아웃 성공"
        })
            
    except Exception as e:
        logger.error(f"로그아웃 처리 중 오류: {str(e)}", exc_info=True)
        return JsonResponse({
            "error": "서버 오류가 발생했습니다."
        }, status=500)

# API 상태 확인
@api_view(["GET"])
@permission_classes([AllowAny])
def api_status(request):
    """
    API 서버 상태 확인 엔드포인트
    
    API 서버가 정상 작동 중인지 확인
    """
    return JsonResponse({
        "status": "online",
        "message": "API 서버가 정상 작동 중입니다."
    }) 