from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging
from .models import Resume
from .groq_service import generate_resume, extract_job_keypoints, log_function_call
from crawlers.Job_Post_Crawler import fetch_job_description
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
import json
from django.http import JsonResponse
from crawlers.Target_Company_Crawler import fetch_company_info
import os
from datetime import datetime
# from django.utils.decorators import method_decorator
import re
import validators  # URL 검증을 위한 라이브러리 추가
import bleach  # 특수문자 필터링을 위한 라이브러리 추가
from django.conf import settings
from django.shortcuts import render
from rest_framework.authtoken.models import Token
import traceback

# 로거 설정 - 환경에 따른 로그 레벨 조정
logger = logging.getLogger('api')
# DEBUG 환경에서는 추가 디버그 로깅
if settings.DEBUG:
    logger.debug("=== 디버그 모드에서 API 모듈 시작 ===")

# 자기소개서 전용 로거 설정
resume_logger = logging.getLogger("resume")

# URL 검증 함수
def validate_url(url):
    """URL 유효성을 검증하는 함수"""
    if not url:
        return False, "URL이 비어있습니다"
    
    # URL 형식 검증
    if not validators.url(url):
        return False, "유효하지 않은 URL 형식입니다"
    
    # 허용된 도메인 목록 (예시)
    allowed_domains = ['saramin.co.kr', 'jobkorea.co.kr', 'wanted.co.kr', 'linkedin.com']
    
    # 도메인 추출을 위한 정규식
    domain_pattern = re.compile(r'^https?://(?:www\.)?([^/]+)')
    match = domain_pattern.match(url)
    
    if not match:
        return False, "도메인을 추출할 수 없습니다"
    
    domain = match.group(1)
    
    # 허용된 도메인인지 확인 (선택적)
    # if not any(domain.endswith(allowed_domain) for allowed_domain in allowed_domains):
    #     return False, f"허용되지 않은 도메인입니다: {domain}"
    
    return True, "유효한 URL입니다"

# 사용자 입력 정제 함수
def sanitize_input(text):
    """사용자 입력에서 잠재적으로 위험한 HTML을 제거하는 함수"""
    if not text:
        return ""
    
    # HTML 태그 및 위험한 속성 제거
    cleaned_text = bleach.clean(
        text,
        tags=[],  # 허용된 HTML 태그 없음
        attributes={},  # 허용된 HTML 속성 없음
        strip=True  # 허용되지 않은 태그 제거
    )
    
    return cleaned_text

# 자기소개서 로깅 함수
def log_resume(resume_id, generated_resume):
    """
    생성된 자기소개서를 Django 로깅 시스템을 통해 기록하는 함수
    """
    try:
        # resume 로거 가져오기
        resume_logger = logging.getLogger('resume')
        
        # 현재 시간
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 민감 정보 마스킹 처리
        masked_resume = generated_resume
        # 이메일 마스킹
        email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
        masked_resume = email_pattern.sub('[MASKED_EMAIL]', masked_resume)
        
        # 전화번호 마스킹
        phone_pattern = re.compile(r'\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4}')
        masked_resume = phone_pattern.sub('[MASKED_PHONE]', masked_resume)
        
        # 로그 메시지 구성
        log_message = f"""
==================================================
[RESUME ID: {resume_id}] - {now}
==================================================
{masked_resume}
==================================================
"""
        
        # 로그 레벨에 따라 기록
        resume_logger.info(f"자기소개서 생성 완료 - ID: {resume_id}")
        resume_logger.debug(log_message)
        
        return True
    except Exception as e:
        resume_logger.error(f"자기소개서 로깅 실패: {str(e)}", exc_info=True)
        return False

@csrf_protect
@api_view(['POST'])
@permission_classes([AllowAny])
def fetch_company_info(request):
    """
    회사 정보를 크롤링하는 API 엔드포인트
    """
    logger.debug("===== fetch_company_info_api 요청 시작 =====")
    if request.method == "POST":
        try:
            # 요청 정보를 확인 (개발 환경에서만 상세 로깅)
            if settings.DEBUG:
                logger.debug(f"요청 헤더: {request.headers}")
                logger.debug(f"요청 쿠키: {request.COOKIES}")
                logger.debug(f"요청 본문: {request.body}")    
            else:
                logger.info(f"API 요청: {request.path} - {request.method}")

            # CSRF 토큰 확인
            csrf_cookie = request.COOKIES.get("csrftoken")
            csrf_header = request.headers.get("X-CSRFToken")
            logger.debug(f"서버에서 받은 CSRF 쿠키: {csrf_cookie}")
            logger.debug(f"서버에서 받은 CSRF 헤더: {csrf_header}")
            
            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                logger.error("CSRF 토큰 검증 실패")
                return JsonResponse({"error": "CSRF 토큰이 일치하지 않습니다."}, status=403)
                                
            data = json.loads(request.body)
            company_url = data.get("company_url")
            logger.debug(f"파싱된 JSON 데이터: {data}")

            if not company_url:
                logger.error("회사 URL 누락")
                return JsonResponse({"error": "회사 URL이 제공되지 않았습니다."}, status=400)

            # URL 검증
            is_valid, error_message = validate_url(company_url)
            if not is_valid:
                logger.error(f"URL 검증 실패: {error_message}")
                return JsonResponse({"error": error_message}, status=400)

            # 크롤링 시작 로그
            logger.info(f"Fetching company info for URL: {company_url}")

            try:
                # 회사 정보 크롤링 함수 호출
                logger.debug("크롤링 함수 fetch_company_info 호출 시작")
                company_info = fetch_company_info(company_url)
                logger.debug("크롤링 함수 fetch_company_info 호출 완료")
                logger.info(f"Fetched company info: {company_info[:200]}")  # 크롤링 결과 앞 200자 출력
            except Exception as e:
                logger.error(f"Error while fetching company info: {str(e)}", exc_info=True)
                return JsonResponse({"error": "회사 정보를 가져오는 중 오류 발생"}, status=500)

            logger.debug("회사 정보 API 응답 반환")
            response = JsonResponse({"company_info": company_info}, status=200)
            logger.debug(f"응답 데이터: {company_info[:100]}...")
            logger.debug("===== fetch_company_info_api 요청 완료 =====")
            return response

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {str(e)}", exc_info=True)
            return JsonResponse({"error": "올바른 JSON 형식이 아닙니다."}, status=400)
        except Exception as e:
            logger.error(f"예상치 못한 오류: {str(e)}", exc_info=True)
            return JsonResponse({"error": f"서버 오류: {str(e)}"}, status=500)

    logger.error(f"허용되지 않은 HTTP 메서드: {request.method}")
    return JsonResponse({"error": "허용되지 않은 요청 방식입니다."}, status=405)


@csrf_exempt
@api_view(["OPTIONS", "POST", "GET"])  #  OPTIONS 요청 허용 (CORS 문제 해결)
@permission_classes([AllowAny])  # 인증된 사용자만 API 호출 가능하도록 설정
# @ensure_csrf_cookie  # CSRF 쿠키를 설정하는 데코레이터 (먼저 적용)
# @csrf_protect  # CSRF 보호 활성화
def create_resume(request):
    logger.debug("===== create_resume 요청 시작 =====")
    logger.debug(f"요청 메서드: {request.method}")
    logger.debug(f"요청 META: {request.META}")
    
    if request.method == "GET":
        logger.debug("GET 요청 처리: CSRF 쿠키 설정")
        # 명시적으로 CSRF 토큰 설정
        csrf_token = get_token(request)
        logger.debug(f"설정된 CSRF 토큰: {csrf_token}")
        response = Response({"message": "CSRF 쿠키 설정됨", "csrf_token": csrf_token}, status=200)
        response.set_cookie("csrftoken", csrf_token)
        return response
    
    logger.info(" API create_resume 요청 수신됨.")
    logger.debug(f" 요청 헤더: {request.headers}")
    logger.debug(f" 요청 본문: {request.data}")
    logger.info(f" 현재 사용자: {request.user} (인증됨 여부: {request.user.is_authenticated})")

    #  CSRF 정보 확인
    csrf_token = get_token(request)  # 올바른 방법으로 토큰 가져오기
    logger.debug(f" CSRF 쿠키: {request.COOKIES.get('csrftoken')}")
    logger.debug(f" CSRF 토큰: {csrf_token}")

    #  403 Forbidden 발생 원인 추적
    if request.user.is_authenticated is False:
        logger.warning(" 로그인되지 않은 사용자 요청 (403 가능성 높음)")

    if "csrftoken" not in request.COOKIES:
        logger.warning(" CSRF 토큰 없음 (403 가능성 높음)")

    try:
        # 클라이언트 요청 데이터 파싱
        logger.debug("클라이언트 요청 데이터 파싱 시작")
        
        # 채용 공고 URL 파싱
        job_url = request.data.get("recruitment_notice_url", "")
        logger.info(f"받은 recruitment_notice_url: {job_url}")
        
        # URL 검증
        is_valid, error_message = validate_url(job_url)
        if not is_valid:
            logger.error(f"채용 공고 URL 검증 실패: {error_message}")
            return Response({"error": error_message}, status=400)
        
        # 회사 URL 파싱
        company_url = request.data.get("target_company_url", "")
        logger.info(f"받은 target_company_url: {company_url}")
        
        # 회사 URL 검증 (제공된 경우)
        if company_url:
            is_valid, error_message = validate_url(company_url)
            if not is_valid:
                logger.error(f"회사 URL 검증 실패: {error_message}")
                return Response({"error": error_message}, status=400)
        
        # 사용자 스토리 파싱
        user_story = request.data.get("user_story", "")
        
        # 사용자 스토리 검증 및 정제
        if isinstance(user_story, str):
            user_story = sanitize_input(user_story)
        elif isinstance(user_story, dict):
            # 딕셔너리 형태인 경우 각 값 정제
            for key in user_story:
                if isinstance(user_story[key], str):
                    user_story[key] = sanitize_input(user_story[key])
        
        # 안전한 로깅을 위해 객체 타입 확인 및 처리
        if isinstance(user_story, dict):
            logger.debug(f"user_story가 딕셔너리입니다: 키={list(user_story.keys())}")
        else:
            logger.debug(f"user_story가 문자열입니다: 길이={len(str(user_story))}")
            logger.debug(f"받은 user_story: {str(user_story)[:100]}...")
        
        # 🔹 채용 공고 크롤링
        logger.debug("채용 공고 크롤링 시작")
        
        try:
            job_description = fetch_job_description(job_url)
            logger.info(f"채용 공고 크롤링 성공: {job_description[:100]}...")
            logger.debug(f"채용 공고 전체 내용: {job_description}")
        except Exception as e:
            logger.error(f"채용 공고 크롤링 실패: {str(e)}", exc_info=True)
            job_description = "(채용 공고 크롤링 실패)"

        # 🔹 회사 정보 크롤링 (company_url이 있을 경우)
        company_info = ""
        if company_url:
            logger.debug("회사 정보 크롤링 시작")
            try:
                company_info = fetch_company_info(company_url)
                logger.info(f"회사 정보 크롤링 성공: {company_info[:100]}...")
                logger.debug(f"회사 정보 전체 내용: {company_info}")
            except Exception as e:
                logger.error(f" 회사 정보 크롤링 실패: {str(e)}", exc_info=True)
                company_info = "(회사 정보 크롤링 실패)"

        # 🔹 크롤링 데이터 검증 (빈 데이터 체크)
        logger.debug("크롤링 데이터 검증")
        if not job_description or job_description == "(채용 공고 크롤링 실패)":
            logger.error("채용 공고 데이터가 없습니다. GPT 호출을 중단합니다.")
            return Response({"error": "채용 공고 데이터를 가져오는 데 실패했습니다."}, status=500)

        if not company_info or company_info == "(회사 정보 크롤링 실패)":
            logger.warning("회사 정보 데이터가 없습니다. GPT는 채용 공고와 사용자 입력만으로 실행됩니다.")


        # 🔹 GPT API 호출하여 자기소개서 생성
        logger.debug("GPT API 호출 준비")
        try:
            logger.info("GPT 호출 직전 데이터:")
            logger.debug(f"🔹 job_description: {job_description[:100]}...")
            
            # 안전한 로깅을 위해 객체 타입 확인
            if isinstance(user_story, dict):
                safe_user_story = str(user_story)[:100]
            else:
                safe_user_story = str(user_story)[:100] if user_story else "None"
                
            logger.debug(f"🔹 user_story: {safe_user_story}...")
            logger.debug(f"🔹 company_info: {company_info[:100]}...")
            
            # 추가: 채용공고 분석 JSON 추출
            logger.info("채용공고 키포인트 추출 시작")
            try:
                job_keypoints_json = extract_job_keypoints(job_description)
                logger.info(f"채용공고 키포인트 추출 성공")
            except Exception as e:
                logger.error(f"채용공고 키포인트 추출 실패: {str(e)}", exc_info=True)
                job_keypoints_json = "{}"
            
            logger.debug("GPT API 호출 시작")
            generated_resume = generate_resume(job_description, user_story, company_info)
            logger.debug("GPT API 호출 완료")
            
            # <think> 태그 제거 (실제 응답에서 제거)
            logger.debug(f"<think> 태그 제거 전 자기소개서 길이: {len(generated_resume)}")
            cleaned_resume = re.sub(r'<think>[\s\S]*?</think>', '', generated_resume, flags=re.DOTALL)
            # 혹시 남아있는 태그 추가 제거
            cleaned_resume = re.sub(r'<think>', '', cleaned_resume)
            cleaned_resume = re.sub(r'</think>', '', cleaned_resume)
            logger.debug(f"<think> 태그 제거 후 자기소개서 길이: {len(cleaned_resume)}")
            
            # 깨끗한 버전을 사용
            generated_resume = cleaned_resume
            
            logger.info(f"GPT 자기소개서 생성 성공: {generated_resume[:100]}...")
            logger.debug(f"생성된 자기소개서 전체: {generated_resume}")
        except Exception as e:
            logger.error(f"GPT API 호출 실패: {str(e)}", exc_info=True)
            return Response({"error": "GPT API 호출 중 문제가 발생했습니다."}, status=500)

        # 🔹 DB 저장
        logger.debug("데이터베이스 저장 시작")
        try:
            resume = Resume.objects.create(
                recruitment_notice_url=job_url,
                target_company_url=company_url,
                job_description=job_description,
                company_info=company_info,
                user_story=user_story,
                generated_resume=generated_resume
            )
            logger.info(f" DB 저장 성공: Resume ID {resume.id}")
            
            # 새로운 코드: Django 로깅 시스템을 통한 자기소개서 로깅
            log_resume(resume.id, generated_resume)
            
        except Exception as e:
            logger.error(f" 데이터베이스 저장 실패: {str(e)}", exc_info=True)
            return Response({"error": "데이터 저장 중 문제가 발생했습니다."}, status=500)

        # 🔹 응답 데이터 반환
        logger.debug("응답 데이터 구성")
        response_data = {
            "resume_id": resume.id,
            "recruitment_notice_url": resume.recruitment_notice_url,
            "target_company_url": resume.target_company_url,
            "user_story": resume.user_story,
            "company_info": resume.company_info,  # 응답에 회사 정보 포함
            "generated_resume": resume.generated_resume,
            "created_at": resume.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

        logger.info(f" 자기소개서 생성 완료: ID {resume.id}")
        logger.debug(f" 응답 데이터: {response_data}")
        logger.debug("===== create_resume 요청 완료 =====")
        return Response(response_data)

    except Exception as e:
        logger.critical(f" 서버 내부 오류 발생: {str(e)}", exc_info=True)
        logger.debug("===== create_resume 요청 실패 =====")
        return Response({"error": "서버에서 오류가 발생했습니다."}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def test_groq_logging(request):
    """
    테스트 목적의 API 엔드포인트
    
    로그 파일에 기록하지 않고 응답으로만 결과를 반환합니다.
    """
    try:
        # 간단한 테스트 데이터
        test_input = request.data or {'test': 'data'}
        
        # 기존 로깅 대신 콘솔에만 출력
        print(f"테스트 로깅 API 호출: {test_input}")
        
        # 채용 공고 분석 테스트 (로그에 기록하지 않음)
        sample_job = '소프트웨어 개발자 모집. 주요 업무는 웹 개발입니다. 필수 자격요건은 Python, JavaScript 경험입니다.'
        from .groq_service import extract_job_keypoints
        
        # 특별히 로그 핸들러를 비활성화
        logger.info("테스트 모드로 GPT 분석 실행 (로그 파일에 기록하지 않음)")
        
        # 로깅 없이 함수만 실행
        result = extract_job_keypoints(sample_job)
        
        return Response({
            'status': 'success',
            'message': '테스트 완료 (로그 파일에 기록되지 않음)',
            'result': result
        })
    except Exception as e:
        logger.error(f"테스트 함수 실행 중 오류: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

def index(request):
    """
    메인 페이지 뷰 - API 키 정보 포함
    """
    try:
        # 디버깅을 위해 정적 파일 경로 확인
        from django.contrib.staticfiles import finders
        from django.conf import settings
        import os
        
        # 폰트 파일 경로 로깅
        font_path = 'fonts/NotoSansKR-Regular.woff2'
        absolute_path = finders.find(font_path)
        logger.debug(f"폰트 파일 경로 검색: {font_path}")
        logger.debug(f"폰트 파일 절대 경로: {absolute_path}")
        logger.debug(f"STATIC_ROOT: {settings.STATIC_ROOT}")
        logger.debug(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        
        # STATICFILES_DIRS에서 직접 파일 존재 확인
        for static_dir in settings.STATICFILES_DIRS:
            full_path = os.path.join(static_dir, font_path)
            exists = os.path.exists(full_path)
            logger.debug(f"폰트 파일 확인 ({static_dir}): {exists}, 경로: {full_path}")
        
        api_key = settings.API_KEY
        return render(request, 'index.html', {'api_key': api_key})
    except Exception as e:
        logger.error(f"인덱스 페이지 렌더링 중 오류: {e}")
        logger.debug(f"상세 오류: {traceback.format_exc()}")
        return render(request, 'error.html', {'error': str(e)})
