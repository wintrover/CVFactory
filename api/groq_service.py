import os
from dotenv import load_dotenv
import groq
import re
import logging
import json
from datetime import datetime
import traceback
import inspect
import sys
from django.conf import settings

# 로거 설정
logger = logging.getLogger("api")

# groq_service 전용 로거 설정
groq_logger = logging.getLogger("groq_service")

# 개발 환경에서만 디버그 메시지 출력
if settings.DEBUG:
    # 파일 핸들러 설정
    log_dir = os.path.join("logs")
    os.makedirs(log_dir, exist_ok=True)  # 로그 디렉토리 확인
    
    groq_handler = logging.FileHandler(os.path.join(log_dir, "groq_service_debug.log"), encoding='utf-8')
    groq_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s] - %(message)s'))
    groq_logger.addHandler(groq_handler)
    
    groq_logger.debug("=== Groq 서비스 디버그 모드로 시작 ===")
    groq_logger.debug(f"로그 레벨: {logging.getLevelName(groq_logger.level)}")

# .env 파일 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'env_configs', '.env'))

# Groq API 키 설정
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    error_msg = "Groq API Key가 설정되지 않았습니다."
    groq_logger.error(error_msg)
    raise ValueError(error_msg)

# 패키지 버전 정보 로깅
groq_logger.info(f"Python 버전: {sys.version}")
groq_logger.info(f"Groq 모듈 버전: {getattr(groq, '__version__', '버전 정보 없음')}")
groq_logger.info(f"Groq 모듈 경로: {getattr(groq, '__file__', '파일 경로 정보 없음')}")

# Groq 클라이언트 초기화
try:
    # 문제의 근본적 원인: groq 모듈의 내부 구현 문제로 인한 'proxies' 파라미터 충돌
    groq_logger.info("Groq Client 초기화를 위한 패치 시도")
    
    # 원본 클래스를 직접 패치하여 proxies 문제 해결
    import types
    from groq import Client
    from groq._client import Groq as OriginalGroq
    
    # 원본 __init__ 메서드 가져오기
    original_init = OriginalGroq.__init__
    
    # 패치 적용 전에 클래스 정보 출력
    groq_logger.debug(f"OriginalGroq 클래스: {OriginalGroq}")
    groq_logger.debug(f"original_init 메서드: {original_init}")
    groq_logger.debug(f"original_init 파라미터: {inspect.signature(original_init)}")
    
    # 모든 인자를 받되 proxies 인자를 무시하는 새로운 __init__ 함수 정의
    def patched_init(self, *args, **kwargs):
        # 원본 kwargs 로깅
        groq_logger.debug(f"patched_init 호출 kwargs: {kwargs}")
        
        # proxies 파라미터 제거
        if 'proxies' in kwargs:
            groq_logger.info(f"proxies 파라미터 제거됨: {kwargs['proxies']}")
            del kwargs['proxies']
            
        # 수정된 kwargs 로깅
        groq_logger.debug(f"수정된 kwargs: {kwargs}")
        
        try:
            result = original_init(self, *args, **kwargs)
            groq_logger.info("원본 __init__ 함수 호출 성공")
            return result
        except Exception as e:
            groq_logger.error(f"원본 __init__ 함수 호출 중 오류 발생: {str(e)}")
            groq_logger.debug(f"오류 상세: {traceback.format_exc()}")
            raise
    
    # 패치 적용
    groq_logger.info("groq.Client 클래스 패치 적용")
    OriginalGroq.__init__ = patched_init
    
    # 패치 적용 후 클라이언트 초기화 시도
    groq_logger.info("패치된 클래스로 클라이언트 초기화 시도")
    
    # 최소한의 필수 인자만으로 초기화 시도
    client_params = {"api_key": api_key}
    groq_logger.debug(f"클라이언트 초기화 파라미터: {client_params}")
    
    client = Client(**client_params)
    groq_logger.info("Groq 클라이언트 초기화 성공 (패치 방식)")
    
    # 테스트 호출로 정상 작동 여부 확인
    groq_logger.info("클라이언트 객체 생성 성공, 테스트 진행")
    
    if client is not None:
        groq_logger.info("Groq 서비스가 성공적으로 초기화되었습니다.")
    else:
        groq_logger.error("Groq 클라이언트가 초기화되지 않았습니다.")

except Exception as e:
    groq_logger.error(f"Groq 클라이언트 초기화 실패: {str(e)}")
    # 로그에 자세한 에러 정보 기록
    groq_logger.debug(f"상세 오류: {traceback.format_exc()}")
    
    # 대체 초기화 방법 시도
    groq_logger.info("대체 초기화 방법 시도")
    try:
        # 첫 번째 대체 방법: http 모듈을 통한 직접 API 호출 설정
        import httpx
        groq_logger.info("httpx를 사용한 대체 클라이언트 설정 시도")
        
        # 사용자 정의 클래스 생성
        class SimpleGroqClient:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.groq.com/v1"
                self.client = httpx.Client(
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )
                self.chat = SimpleGroqChatCompletions(self)
                
            def close(self):
                self.client.close()
                
        class SimpleGroqChatCompletions:
            def __init__(self, parent):
                self.parent = parent
                self.completions = self
                
            def create(self, model, messages, temperature=0.7, max_tokens=None, **kwargs):
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature
                }
                
                if max_tokens:
                    payload["max_tokens"] = max_tokens
                    
                # 추가 파라미터 처리
                for k, v in kwargs.items():
                    if k not in payload and k != "proxies":
                        payload[k] = v
                
                groq_logger.debug(f"API 요청 페이로드: {payload}")
                
                response = self.parent.client.post(
                    f"{self.parent.base_url}/chat/completions",
                    json=payload
                )
                
                if response.status_code != 200:
                    groq_logger.error(f"API 오류: {response.status_code} - {response.text}")
                    raise Exception(f"API 오류: {response.status_code} - {response.text}")
                    
                result = response.json()
                groq_logger.debug(f"API 응답: {result}")
                
                # Groq 스타일의 응답 객체 생성
                class SimpleResponse:
                    def __init__(self, data):
                        self.id = data.get("id")
                        self.object = data.get("object")
                        self.created = data.get("created")
                        self.model = data.get("model")
                        self.choices = [SimpleChoice(c) for c in data.get("choices", [])]
                        self.usage = SimpleUsage(data.get("usage", {}))
                        
                class SimpleChoice:
                    def __init__(self, data):
                        self.index = data.get("index")
                        self.message = SimpleMessage(data.get("message", {}))
                        self.finish_reason = data.get("finish_reason")
                        
                class SimpleMessage:
                    def __init__(self, data):
                        self.role = data.get("role")
                        self.content = data.get("content")
                        
                class SimpleUsage:
                    def __init__(self, data):
                        self.prompt_tokens = data.get("prompt_tokens")
                        self.completion_tokens = data.get("completion_tokens")
                        self.total_tokens = data.get("total_tokens")
                        
                return SimpleResponse(result)
        
        # 새로운 클라이언트 생성
        client = SimpleGroqClient(api_key)
        groq_logger.info("대체 클라이언트 초기화 성공")
            
    except Exception as alt_e:
        groq_logger.error(f"대체 초기화 방법도 실패: {str(alt_e)}")
        groq_logger.debug(f"대체 방법 상세 오류: {traceback.format_exc()}")
        groq_logger.warning("이 오류로 인해 AI 기능이 제한됩니다.")
        # 클라이언트 객체 None으로 설정 - 이 경우 함수들은 fallback 응답 반환
        client = None

def log_function_call(func_name, inputs, outputs=None, additional_info=None):
    """함수 호출 정보를 로깅하는 유틸리티 함수"""
    # 개발 환경에서만 상세 로깅
    if not settings.DEBUG:
        return
        
    log_entry = {
        "function": func_name,
        "timestamp": datetime.now().isoformat(),
        "inputs": inputs,
    }
    
    if outputs:
        log_entry["outputs"] = outputs
        
    if additional_info:
        log_entry["additional_info"] = additional_info
    
    # 안전한 직렬화를 위해 기본 처리
    try:    
        groq_logger.debug(json.dumps(log_entry, ensure_ascii=False, default=str))
    except TypeError as e:
        # 직렬화 불가능한 객체가 있는 경우 str()로 변환
        groq_logger.error(f"로깅 중 직렬화 오류: {e}")
        # 입력을 안전하게 문자열로 변환
        safe_log_entry = {
            "function": str(func_name),
            "timestamp": str(datetime.now().isoformat()),
            "inputs": str(inputs),
        }
        if outputs:
            safe_log_entry["outputs"] = str(outputs)
        if additional_info:
            safe_log_entry["additional_info"] = str(additional_info)
        groq_logger.debug(json.dumps(safe_log_entry, ensure_ascii=False))

def analyze_job_description(job_description):
    """
    1단계-1: 채용공고 분석
    """
    func_name = "analyze_job_description"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    groq_logger.debug(f"입력 파라미터: job_description 길이 = {len(job_description)}")
    
    # 입력 로깅
    inputs = {"job_description_length": len(job_description), "job_description_preview": job_description[:100] + "..."}
    log_function_call(func_name, inputs)
    
    prompt = f"""
    다음 채용공고를 분석해주세요:
    
    채용공고:
    {job_description}
    
    다음 사항을 분석해주세요:
    1. 주요 업무 내용
    2. 필수 자격 요건
    3. 우대 사항
    4. 직무 특성
    """
    
    groq_logger.debug(f"생성된 프롬프트 길이: {len(prompt)}")
    
    try:
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 채용공고 분석 전문가입니다. 주어진 채용공고의 주요 내용을 분석해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            job_analysis = response.choices[0].message.content
            
            # 출력 및 처리 과정 로깅
            additional_info = {
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
            }
            outputs = {"job_analysis_length": len(job_analysis), "job_analysis_preview": job_analysis[:100] + "..."}
            log_function_call(func_name, inputs, outputs, additional_info)
            
            logger.info(f"채용공고 분석 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            groq_logger.info(f"===== {func_name} 함수 종료 =====")
            return job_analysis
        else:
            error_msg = f"채용공고 분석 API 응답 형식 오류: {response}"
            logger.error(error_msg)
            groq_logger.error(error_msg)
            
            # 오류 로깅
            outputs = {"error": error_msg}
            log_function_call(func_name, inputs, outputs)
            
            groq_logger.info(f"===== {func_name} 함수 종료 (오류) =====")
            return "채용공고 분석 중 오류가 발생했습니다."
            
    except Exception as e:
        error_msg = f"채용공고 분석 API 호출 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # 스택 트레이스 포함하여 오류 로깅
        outputs = {"error": str(e), "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return "채용공고 분석 중 오류가 발생했습니다."

def analyze_company_info(company_info):
    """
    1단계-2: 회사 정보 분석
    """
    func_name = "analyze_company_info"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    groq_logger.debug(f"입력 파라미터: company_info 길이 = {len(company_info)}")
    
    # 입력 로깅
    inputs = {"company_info_length": len(company_info), "company_info_preview": company_info[:100] + "..."}
    log_function_call(func_name, inputs)
    
    logger.info(f"[DEBUG] analyze_company_info 시작 - 입력 길이: {len(company_info)}")
    prompt = f"""
    다음 회사 정보를 분석해주세요:
    
    회사 정보:
    {company_info}
    
    다음 사항을 분석해주세요:
    1. 회사의 주요 사업 영역
    2. 회사 문화와 가치관
    3. 회사의 성장성과 미래 전망
    """
    
    groq_logger.debug(f"생성된 프롬프트 길이: {len(prompt)}")
    
    try:
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 회사 분석 전문가입니다. 주어진 회사 정보의 주요 내용을 분석해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            company_analysis = response.choices[0].message.content
            
            # 출력 및 처리 과정 로깅
            additional_info = {
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
            }
            outputs = {"company_analysis_length": len(company_analysis), "company_analysis_preview": company_analysis[:100] + "..."}
            log_function_call(func_name, inputs, outputs, additional_info)
            
            logger.info(f"회사 정보 분석 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            groq_logger.info(f"===== {func_name} 함수 종료 =====")
            return company_analysis
        else:
            error_msg = f"회사 정보 분석 API 응답 형식 오류: {response}"
            logger.error(error_msg)
            groq_logger.error(error_msg)
            
            # 오류 로깅
            outputs = {"error": error_msg}
            log_function_call(func_name, inputs, outputs)
            
            groq_logger.info(f"===== {func_name} 함수 종료 (오류) =====")
            return "회사 정보 분석 중 오류가 발생했습니다."
            
    except Exception as e:
        error_msg = f"회사 정보 분석 API 호출 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # 스택 트레이스 포함하여 오류 로깅
        outputs = {"error": str(e), "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return "회사 정보 분석 중 오류가 발생했습니다."

def analyze_job_and_company(job_description, company_info):
    """
    1단계: 채용공고와 회사 정보 분석
    """
    func_name = "analyze_job_and_company"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    
    # 입력 로깅
    inputs = {
        "job_description_length": len(job_description),
        "company_info_length": len(company_info),
        "job_description_preview": job_description[:100] + "...",
        "company_info_preview": company_info[:100] + "..."
    }
    log_function_call(func_name, inputs)
    
    try:
        # 1단계-1: 채용공고 분석
        groq_logger.debug("1단계-1: 채용공고 분석 시작")
        logger.debug("1단계-1: 채용공고 분석 시작")
        job_analysis = analyze_job_description(job_description)
        logger.debug(f"채용공고 분석: {job_analysis[:100]}...")
        groq_logger.debug(f"채용공고 분석 결과 길이: {len(job_analysis)}")
        
        # 1단계-2: 회사 정보 분석
        groq_logger.debug("1단계-2: 회사 정보 분석 시작")
        logger.debug("1단계-2: 회사 정보 분석 시작")
        company_analysis = analyze_company_info(company_info)
        logger.debug(f"회사 정보 분석: {company_analysis[:100]}...")
        groq_logger.debug(f"회사 정보 분석 결과 길이: {len(company_analysis)}")
        
        # 분석 결과 통합
        analysis = f"""
        [채용공고 분석]
        {job_analysis}
        
        [회사 정보 분석]
        {company_analysis}
        """
        
        # 출력 및 처리 과정 로깅
        outputs = {
            "analysis_length": len(analysis),
            "analysis_preview": analysis[:100] + "..."
        }
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.info(f"===== {func_name} 함수 종료 =====")
        return analysis
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"채용공고/회사 분석 중 오류 발생: {error_msg}", exc_info=True)
        
        # 오류 로깅
        outputs = {"error": error_msg, "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(f"채용공고/회사 분석 중 오류 발생: {error_msg}")
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return "채용공고/회사 분석 중 오류가 발생했습니다."

def extract_job_keypoints(job_description):
    """
    채용공고에서 핵심 내용만 추출
    """
    func_name = "extract_job_keypoints"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    
    # 안전한 입력 준비
    if job_description is None:
        job_description = ""
        
    # 문자열 확인 및 변환
    if not isinstance(job_description, str):
        logger.warning(f"job_description이 문자열이 아닙니다: {type(job_description)}")
        job_description = str(job_description)
    
    # 입력 로깅 - 안전한 슬라이싱
    job_desc_preview = job_description[:100] + "..." if len(job_description) > 100 else job_description
    inputs = {"job_description_length": len(job_description), "job_description_preview": job_desc_preview}
    log_function_call(func_name, inputs)
    
    try:
        logger.debug(f"=== extract_job_keypoints 시작 ===")
        logger.debug(f"입력 job_description 길이: {len(job_description)}")
        groq_logger.debug(f"입력 job_description 길이: {len(job_description)}")
        
        prompt = f"""다음 채용공고에서 핵심 내용만 추출해주세요:

채용공고:
{job_description}

다음 형식으로 추출해주세요:
1. 주요 업무 (3-4줄)
2. 필수 자격요건 (3-4줄)
3. 우대사항 (2-3줄)"""

        logger.debug(f"프롬프트 길이: {len(prompt)}")
        groq_logger.debug(f"생성된 프롬프트 길이: {len(prompt)}")
        
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        logger.debug(f"응답 토큰 수: {response.usage.completion_tokens}")
        logger.debug(f"=== extract_job_keypoints 완료 ===")
        
        result = response.choices[0].message.content
        
        # 출력 및 처리 과정 로깅
        additional_info = {
            "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
            "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
            "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
        }
        outputs = {"result_length": len(result), "result_preview": result[:100] + "..."}
        log_function_call(func_name, inputs, outputs, additional_info)
        
        groq_logger.info(f"===== {func_name} 함수 종료 =====")
        return result
    except Exception as e:
        error_msg = f"extract_job_keypoints 오류: {str(e)}"
        logger.error(error_msg)
        
        # 오류 로깅
        outputs = {"error": str(e), "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        raise

def create_resume_draft(job_keypoints, company_info, user_story):
    """
    2단계: 자기소개서 초안 작성
    """
    func_name = "create_resume_draft"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    
    # 입력 타입 검증 및 변환
    if not isinstance(job_keypoints, str):
        job_keypoints = str(job_keypoints)
    
    if not isinstance(company_info, str):
        company_info = str(company_info)
        
    # user_story 처리 개선
    user_story_dict = {}
    if isinstance(user_story, dict):
        user_story_dict = user_story
    elif isinstance(user_story, str):
        logger.warning(f"user_story가 문자열입니다: {type(user_story)}")
        # 문자열을 분석하여 기본 정보 추출 시도
        user_story_dict = {
            '성격의 장단점': user_story,
            '지원 동기': user_story,
            '입사 후 포부': user_story
        }
    else:
        logger.warning(f"user_story가 예상치 못한 타입입니다: {type(user_story)}")
        user_story_dict = {
            '성격의 장단점': str(user_story),
            '지원 동기': str(user_story),
            '입사 후 포부': str(user_story)
        }
    
    # 안전한 슬라이싱을 위한 프리뷰 생성
    job_preview = job_keypoints[:100] + "..." if len(job_keypoints) > 100 else job_keypoints
    company_preview = company_info[:100] + "..." if len(company_info) > 100 else company_info
    
    # 입력 로깅
    inputs = {
        "job_keypoints_length": len(job_keypoints),
        "company_info_length": len(company_info),
        "user_story_keys": list(user_story_dict.keys()),
        "job_keypoints_preview": job_preview,
        "company_info_preview": company_preview
    }
    log_function_call(func_name, inputs)
    
    # 성장과정과 학교생활 제거
    filtered_story = {
        '성격의 장단점': user_story_dict.get('성격의 장단점', ''),
        '지원 동기': user_story_dict.get('지원 동기', ''),
        '입사 후 포부': user_story_dict.get('입사 후 포부', '')
    }
    
    groq_logger.debug(f"필터링된 user_story 키: {list(filtered_story.keys())}")
    
    prompt = f"""
    다음 정보를 바탕으로 자기소개서를 작성해주세요:
    
    [채용공고 핵심 내용]
    {job_keypoints}
    
    [회사 정보]
    {company_info}
    
    [지원자 정보]
    성격의 장단점: {filtered_story['성격의 장단점']}
    지원 동기: {filtered_story['지원 동기']}
    입사 후 포부: {filtered_story['입사 후 포부']}
    
    다음 사항을 포함하여 작성해주세요:
    1. 지원자의 핵심 경쟁력과 지원 동기
    2. 회사와 직무에 대한 이해도
    3. 입사 후 기여 방안
    """
    
    groq_logger.debug(f"생성된 프롬프트 길이: {len(prompt)}")
    
    try:
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 작성 전문가입니다. 주어진 정보를 바탕으로 설득력 있는 자기소개서를 작성해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            draft = response.choices[0].message.content
            
            # 출력 및 처리 과정 로깅
            additional_info = {
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
            }
            outputs = {"draft_length": len(draft), "draft_preview": draft[:100] + "..."}
            log_function_call(func_name, inputs, outputs, additional_info)
            
            logger.info(f"자기소개서 초안 작성 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            groq_logger.info(f"===== {func_name} 함수 종료 =====")
            return draft
        else:
            error_msg = f"자기소개서 초안 작성 API 응답 형식 오류: {response}"
            logger.error(error_msg)
            
            # 오류 로깅
            outputs = {"error": error_msg}
            log_function_call(func_name, inputs, outputs)
            
            groq_logger.error(error_msg)
            groq_logger.info(f"===== {func_name} 함수 종료 (오류) =====")
            return "자기소개서 초안 작성 중 오류가 발생했습니다."
            
    except Exception as e:
        error_msg = f"자기소개서 초안 작성 API 호출 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # 오류 로깅
        outputs = {"error": str(e), "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return "자기소개서 초안 작성 중 오류가 발생했습니다."

def finalize_resume_metrics(resume_draft):
    """
    3단계-1: 성과와 역량을 구체적 수치로 표현
    """
    func_name = "finalize_resume_metrics"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    
    # 입력 로깅
    inputs = {"resume_draft_length": len(resume_draft), "resume_draft_preview": resume_draft[:100] + "..."}
    log_function_call(func_name, inputs)
    
    prompt = f"""
    다음 자기소개서 초안의 성과와 역량을 구체적 수치로 표현해주세요:
    
    초안: {resume_draft}
    
    다음 사항을 개선해주세요:
    1. 모든 성과와 역량은 구체적 수치로 표현 (예: "생산성 30% 향상", "만족도 4.8/5 달성")
    2. 입사 시 예상 기여도를 수치로 제시 (예: "비용 40% 절감", "매출 15% 성장 기여")
    """
    
    groq_logger.debug(f"생성된 프롬프트 길이: {len(prompt)}")
    
    try:
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 편집 전문가입니다. 주어진 초안의 성과와 역량을 구체적 수치로 표현해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            metrics = response.choices[0].message.content
            
            # 출력 및 처리 과정 로깅
            additional_info = {
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
            }
            outputs = {"metrics_length": len(metrics), "metrics_preview": metrics[:100] + "..."}
            log_function_call(func_name, inputs, outputs, additional_info)
            
            logger.info(f"자기소개서 수치화 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            groq_logger.info(f"===== {func_name} 함수 종료 =====")
            return metrics
        else:
            error_msg = f"수치화 API 응답 형식 오류: {response}"
            logger.error(error_msg)
            
            # 오류 로깅
            outputs = {"error": error_msg}
            log_function_call(func_name, inputs, outputs)
            
            groq_logger.error(error_msg)
            groq_logger.info(f"===== {func_name} 함수 종료 (오류) =====")
            return "자기소개서 수치화 중 오류가 발생했습니다."
            
    except Exception as e:
        error_msg = f"수치화 API 호출 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # 오류 로깅
        outputs = {"error": str(e), "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return "자기소개서 수치화 중 오류가 발생했습니다."

def finalize_resume_style(resume_draft):
    """
    3단계-2: 전문성과 열정을 강조하는 문체로 수정
    """
    func_name = "finalize_resume_style"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    
    # 입력 로깅
    inputs = {"resume_draft_length": len(resume_draft), "resume_draft_preview": resume_draft[:100] + "..."}
    log_function_call(func_name, inputs)
    
    prompt = f"""
    다음 자기소개서 초안을 전문성과 열정을 강조하는 문체로 수정해주세요:
    
    초안: {resume_draft}
    
    다음 사항을 개선해주세요:
    1. 전문 용어와 업계 용어를 자연스럽게 사용
    2. 열정과 자신감을 표현하는 어조 사용
    3. 간결하고 명확한 문장으로 수정
    """
    
    groq_logger.debug(f"생성된 프롬프트 길이: {len(prompt)}")
    
    try:
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 편집 전문가입니다. 주어진 초안을 전문성과 열정을 강조하는 문체로 수정해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            styled = response.choices[0].message.content
            
            # 출력 및 처리 과정 로깅
            additional_info = {
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
            }
            outputs = {"styled_length": len(styled), "styled_preview": styled[:100] + "..."}
            log_function_call(func_name, inputs, outputs, additional_info)
            
            logger.info(f"자기소개서 문체 수정 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            groq_logger.info(f"===== {func_name} 함수 종료 =====")
            return styled
        else:
            error_msg = f"문체 수정 API 응답 형식 오류: {response}"
            logger.error(error_msg)
            
            # 오류 로깅
            outputs = {"error": error_msg}
            log_function_call(func_name, inputs, outputs)
            
            groq_logger.error(error_msg)
            groq_logger.info(f"===== {func_name} 함수 종료 (오류) =====")
            return "자기소개서 문체 수정 중 오류가 발생했습니다."
            
    except Exception as e:
        error_msg = f"문체 수정 API 호출 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # 오류 로깅
        outputs = {"error": str(e), "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return "자기소개서 문체 수정 중 오류가 발생했습니다."

def finalize_resume_emphasis(resume_draft):
    """
    3단계-3: 직무 관련 핵심 키워드 강조 및 맞춤화
    """
    func_name = "finalize_resume_emphasis"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    
    # 입력 로깅
    inputs = {"resume_draft_length": len(resume_draft), "resume_draft_preview": resume_draft[:100] + "..."}
    log_function_call(func_name, inputs)
    
    prompt = f"""
    다음 자기소개서 초안에서 직무 관련 핵심 키워드를 강조하고 맞춤화해주세요:
    
    초안: {resume_draft}
    
    다음 사항을 개선해주세요:
    1. 직무 관련 핵심 키워드 3-5개 강조 (굵은 글씨로 표시하지 말고, 문맥 속에 자연스럽게 강조)
    2. 회사 문화와 가치관과 일치하는 내용으로 맞춤화
    3. 지원 포지션에 꼭 필요한 역량 중심으로 재구성
    """
    
    groq_logger.debug(f"생성된 프롬프트 길이: {len(prompt)}")
    
    try:
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 편집 전문가입니다. 주어진 초안에서 직무 관련 핵심 키워드를 강조하고 맞춤화해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            emphasized = response.choices[0].message.content
            
            # 출력 및 처리 과정 로깅
            additional_info = {
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
            }
            outputs = {"emphasized_length": len(emphasized), "emphasized_preview": emphasized[:100] + "..."}
            log_function_call(func_name, inputs, outputs, additional_info)
            
            logger.info(f"자기소개서 키워드 강조 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            groq_logger.info(f"===== {func_name} 함수 종료 =====")
            return emphasized
        else:
            error_msg = f"키워드 강조 API 응답 형식 오류: {response}"
            logger.error(error_msg)
            
            # 오류 로깅
            outputs = {"error": error_msg}
            log_function_call(func_name, inputs, outputs)
            
            groq_logger.error(error_msg)
            groq_logger.info(f"===== {func_name} 함수 종료 (오류) =====")
            return "자기소개서 키워드 강조 중 오류가 발생했습니다."
            
    except Exception as e:
        error_msg = f"키워드 강조 API 호출 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # 오류 로깅
        outputs = {"error": str(e), "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return "자기소개서 키워드 강조 중 오류가 발생했습니다."

def finalize_resume(resume_draft):
    """
    3단계: 자기소개서 최종 완성
    """
    func_name = "finalize_resume"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    
    # 입력 타입 검증
    if not isinstance(resume_draft, str):
        logger.warning(f"resume_draft가 문자열이 아닙니다: {type(resume_draft)}")
        resume_draft = str(resume_draft)
    
    # 안전한 프리뷰 생성
    draft_preview = resume_draft[:100] + "..." if len(resume_draft) > 100 else resume_draft
    
    # 입력 로깅
    inputs = {"resume_draft_length": len(resume_draft), "resume_draft_preview": draft_preview}
    log_function_call(func_name, inputs)
    
    try:
        groq_logger.debug("3단계-1: 성과와 역량을 구체적 수치로 표현 시작")
        # 3단계-1: 성과와 역량을 구체적 수치로 표현
        metrics = finalize_resume_metrics(resume_draft)
        groq_logger.debug(f"수치화 결과 길이: {len(metrics)}")
        
        groq_logger.debug("3단계-2: 전문성과 열정을 강조하는 문체로 수정 시작")
        # 3단계-2: 전문성과 열정을 강조하는 문체로 수정
        styled = finalize_resume_style(metrics)
        groq_logger.debug(f"문체 수정 결과 길이: {len(styled)}")
        
        groq_logger.debug("3단계-3: 직무 관련 핵심 키워드 강조 및 맞춤화 시작")
        # 3단계-3: 직무 관련 핵심 키워드 강조 및 맞춤화
        finalized = finalize_resume_emphasis(styled)
        groq_logger.debug(f"키워드 강조 결과 길이: {len(finalized)}")
        
        # 출력 및 처리 과정 로깅
        outputs = {
            "finalized_length": len(finalized),
            "finalized_preview": finalized[:100] + "..."
        }
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.info(f"===== {func_name} 함수 종료 =====")
        return finalized
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"자기소개서 최종 완성 중 오류 발생: {error_msg}", exc_info=True)
        
        # 오류 로깅
        outputs = {"error": error_msg, "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(f"자기소개서 최종 완성 중 오류 발생: {error_msg}")
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return "자기소개서 최종 완성 중 오류가 발생했습니다."

def generate_resume(job_description, user_story, company_info):
    """
    자기소개서 생성 - 단일 API 호출로 통합
    """
    func_name = "generate_resume"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    
    # 입력 타입 검증
    if not isinstance(job_description, str):
        logger.warning(f"job_description이 문자열이 아닙니다: {type(job_description)}")
        job_description = str(job_description)
        
    if not isinstance(company_info, str):
        logger.warning(f"company_info가 문자열이 아닙니다: {type(company_info)}")
        company_info = str(company_info)
    
    # user_story 처리 개선
    user_story_dict = {}
    if isinstance(user_story, dict):
        user_story_dict = user_story
    elif isinstance(user_story, str):
        logger.warning(f"user_story가 문자열입니다: {type(user_story)}")
        # 문자열을 분석하여 기본 정보 추출 시도
        user_story_dict = {
            '성격의 장단점': user_story,
            '지원 동기': user_story,
            '입사 후 포부': user_story
        }
    else:
        logger.warning(f"user_story가 예상치 못한 타입입니다: {type(user_story)}")
        user_story_dict = {
            '성격의 장단점': str(user_story),
            '지원 동기': str(user_story),
            '입사 후 포부': str(user_story)
        }
    
    # 안전한 프리뷰 생성
    job_preview = job_description[:100] + "..." if len(job_description) > 100 else job_description
    company_preview = company_info[:100] + "..." if len(company_info) > 100 else company_info
    
    # 입력 로깅
    inputs = {
        "job_description_length": len(job_description),
        "company_info_length": len(company_info),
        "user_story_keys": list(user_story_dict.keys()),
        "job_description_preview": job_preview,
        "company_info_preview": company_preview
    }
    log_function_call(func_name, inputs)
    
    # 통합 프롬프트 구성 - 모든 단계를 하나의 프롬프트로 통합
    filtered_story = {
        '성격의 장단점': user_story_dict.get('성격의 장단점', ''),
        '지원 동기': user_story_dict.get('지원 동기', ''),
        '입사 후 포부': user_story_dict.get('입사 후 포부', '')
    }
    
    prompt = f"""
    다음 정보를 바탕으로 완성된 자기소개서를 작성해주세요:
    
    [채용공고]
    {job_description}
    
    [회사 정보]
    {company_info}
    
    [지원자 정보]
    성격의 장단점: {filtered_story['성격의 장단점']}
    지원 동기: {filtered_story['지원 동기']}
    입사 후 포부: {filtered_story['입사 후 포부']}
    
    다음 사항을 포함하는 완성도 높은 자기소개서를 작성해주세요:
    1. 지원자의 핵심 경쟁력과 지원 동기
    2. 회사와 직무에 대한 이해도
    3. 입사 후 기여 방안
    4. 성과와 역량은 구체적 수치로 표현 (예: "생산성 30% 향상", "만족도 4.8/5 달성")
    5. 전문 용어와 업계 용어를 자연스럽게 사용하고 열정과 자신감을 표현하는 어조 사용
    6. 직무 관련 핵심 키워드를 3-5개 자연스럽게 강조
    7. 회사 문화와 가치관과 일치하는 내용 강조
    """
    
    groq_logger.debug(f"생성된 통합 프롬프트 길이: {len(prompt)}")
    
    try:
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b (단일 API 호출 방식)")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 작성 전문가입니다. 채용공고와 회사 정보를 분석하여 지원자 정보를 바탕으로 완성도 높은 자기소개서를 작성해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            finalized_resume = response.choices[0].message.content
            
            # 출력 및 처리 과정 로깅
            additional_info = {
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
            }
            outputs = {
                "finalized_resume_length": len(finalized_resume),
                "finalized_resume_preview": finalized_resume[:100] + "..."
            }
            log_function_call(func_name, inputs, outputs, additional_info)
            
            logger.info(f"자기소개서 생성 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            groq_logger.info(f"===== {func_name} 함수 종료 =====")
            return finalized_resume
        else:
            error_msg = f"자기소개서 생성 API 응답 형식 오류: {response}"
            logger.error(error_msg)
            
            # 오류 로깅
            outputs = {"error": error_msg}
            log_function_call(func_name, inputs, outputs)
            
            groq_logger.error(error_msg)
            groq_logger.info(f"===== {func_name} 함수 종료 (오류) =====")
            return "자기소개서 생성 중 오류가 발생했습니다."
            
    except Exception as e:
        error_msg = f"자기소개서 생성 API 호출 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # 오류 로깅
        outputs = {"error": str(e), "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return "자기소개서 생성 중 오류가 발생했습니다."
