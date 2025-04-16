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

# 로깅 설정 (간소화)
logger = logging.getLogger(__name__)
groq_logger = logging.getLogger('groq_service')

# .env 파일 로드 - 경로 수정
# 기존: load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'env_configs', '.env'))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
groq_logger.debug(f".env 파일 로드 시도 경로: {os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')}")

# Groq API 키 설정
api_key = os.getenv("GROQ_API_KEY")
groq_logger.debug(f"로드된 API 키: {api_key[:5]}..." if api_key else "API 키가 로드되지 않음")

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
    """
    함수 호출 정보를 로깅하는 유틸리티 함수
    """
    try:
        # 로깅 시간 설정
        timestamp = datetime.now().isoformat()
        
        # 로그 데이터 구성
        log_data = {
            "function": func_name,
            "timestamp": timestamp,
            "inputs": inputs
        }
        
        # 출력 데이터가 있는 경우 추가
        if outputs:
            log_data["outputs"] = outputs
            
        # 추가 정보가 있는 경우 추가
        if additional_info:
            for key, value in additional_info.items():
                log_data[key] = value
        
        # JSON 형식으로 로깅
        groq_logger.debug(json.dumps(log_data, ensure_ascii=False))
        return True
    except Exception as e:
        groq_logger.error(f"함수 호출 로깅 실패: {str(e)}")
        return False

def extract_job_keypoints(job_description):
    """
    채용 공고에서 주요 정보 추출 (직무명, 회사명, 근무지 등)
    """
    func_name = "extract_job_keypoints"
    groq_logger.info(f"===== {func_name} 함수 시작 =====")
    
    # 입력 로깅
    inputs = {
        "job_description_length": len(job_description),
        "job_description_preview": job_description[:150] + "..." if len(job_description) > 150 else job_description
    }
    log_function_call(func_name, inputs)
    
    # 주요 정보 추출을 위한 프롬프트 구성
    prompt = f"""
    다음 채용 공고에서 주요 정보를 추출해주세요:
    
    [채용 공고]
    {job_description}
    
    다음 JSON 형식으로 출력해주세요:
    
    ```json
    {{
        "job_title": "직무명",
        "company_name": "회사명",
        "location": "근무지",
        "employment_type": "고용 형태(정규직, 계약직, 인턴 등)",
        "requirements": [
            "필수 요구사항1",
            "필수 요구사항2",
            "..."
        ],
        "preferred": [
            "우대 사항1",
            "우대 사항2",
            "..."
        ],
        "responsibilities": [
            "주요 업무1",
            "주요 업무2",
            "..."
        ],
        "benefits": [
            "복리후생1", 
            "복리후생2",
            "..."
        ],
        "qualifications": [
            "자격 요건1",
            "자격 요건2",
            "..."
        ],
        "keywords": [
            "키워드1",
            "키워드2",
            "..."
        ]
    }}
    ```
    
    반드시 위 형식의 JSON만 출력하고, 다른 텍스트는 포함하지 마세요.
    공고에 해당 정보가 없는 경우 해당 필드를 빈 배열 또는 빈 문자열로 설정하세요.
    """
    
    groq_logger.debug(f"생성된 프롬프트 길이: {len(prompt)}")
    
    try:
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 채용 공고에서 주요 정보를 추출하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        # 응답 전체를 JSON으로 로깅
        try:
            response_json = {
                "id": response.id,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content
                        },
                        "finish_reason": choice.finish_reason
                    } for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if hasattr(response, 'usage') else {}
            }
            groq_logger.info(f"채용공고 키포인트 추출 API 응답 JSON: {json.dumps(response_json, ensure_ascii=False)}")
        except Exception as e:
            groq_logger.error(f"채용공고 응답 JSON 변환 오류: {str(e)}")
            
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            raw_output = response.choices[0].message.content
            
            # JSON 문자열에서 코드 블록 표시 제거
            if "```json" in raw_output or "```" in raw_output:
                raw_output = re.sub(r'```(?:json)?\n?', '', raw_output)
                raw_output = re.sub(r'```', '', raw_output)
            
            # 출력이 실제 JSON인지 확인
            try:
                json_data = json.loads(raw_output.strip())
                
                # 출력 로깅
                outputs = {
                    "extracted_json": json.dumps(json_data, ensure_ascii=False)[:200] + "...",
                    "keys": list(json_data.keys())
                }
                
                # 추가 정보 로깅
                additional_info = {
                    "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None
                }
                
                log_function_call(func_name, inputs, outputs, additional_info)
                
                logger.info(f"채용공고 키포인트 추출 성공")
                groq_logger.info(f"===== {func_name} 함수 종료 =====")
                
                return json.dumps(json_data, ensure_ascii=False)
            except json.JSONDecodeError as e:
                error_msg = f"JSON 파싱 오류: {str(e)}"
                logger.error(error_msg)
                groq_logger.error(error_msg)
                
                outputs = {"error": "JSON 파싱 실패", "raw_output": raw_output[:200] + "..."}
                log_function_call(func_name, inputs, outputs)
                
                # 기본 JSON 구조 반환
                groq_logger.info(f"===== {func_name} 함수 종료 (오류) =====")
                return '{}'
        else:
            error_msg = f"API 응답 형식 오류: {response}"
            logger.error(error_msg)
            
            outputs = {"error": "API 응답 형식 오류"}
            log_function_call(func_name, inputs, outputs)
            
            groq_logger.error(error_msg)
            groq_logger.info(f"===== {func_name} 함수 종료 (오류) =====")
            return '{}'
    except Exception as e:
        error_msg = f"API 호출 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        outputs = {"error": str(e), "traceback": traceback.format_exc()}
        log_function_call(func_name, inputs, outputs)
        
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        groq_logger.info(f"===== {func_name} 함수 종료 (예외) =====")
        return '{}'

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
    
    # user_story 처리 (문자열 또는 딕셔너리 지원)
    user_story_content = ""
    if isinstance(user_story, dict):
        # 딕셔너리인 경우 값들을 합쳐서 문자열로 변환
        for key, value in user_story.items():
            user_story_content += f"{key}: {value}\n"
    elif isinstance(user_story, str):
        logger.info(f"user_story가 문자열입니다: {type(user_story)}")
        user_story_content = user_story
    else:
        logger.warning(f"user_story가 예상치 못한 타입입니다: {type(user_story)}")
        user_story_content = str(user_story)

    # 입력 로깅
    inputs = {
        "job_description_length": len(job_description),
        "company_info_length": len(company_info),
        "user_story_length": len(user_story_content),
        "job_description": job_description,
        "company_info": company_info,
        "user_story": user_story_content
    }
    log_function_call(func_name, inputs)
    
    # 1단계: 사용자 스토리에서 키포인트 추출
    groq_logger.info("사용자 스토리에서 키포인트 추출 시작")
    try:
        keypoints_prompt = f"""
        다음 사용자 스토리를 분석하여 자기소개서 작성에 활용할 수 있는 주요 키포인트를 추출해주세요.
        키포인트는 미리 정해진 카테고리에 한정되지 않고, 사용자 스토리에서 자기소개서 작성에 도움이 될 만한 모든 중요 정보를 포함해야 합니다.
        
        [사용자 스토리]
        {user_story_content}
        
        주체적으로 판단하여 자기소개서에 반영할만한 정보를 찾고, 이를 JSON 형식으로 구조화해주세요.
        키와 값을 자유롭게 결정하되, 각 키포인트의 종류와 내용이 명확히 구분되도록 해주세요.
        
        예를 들어, 다음과 같은 형식이 될 수 있습니다 (이에 한정되지 않음):
        ```
        {{
          "핵심_강점": "...",
          "관련_경험": ["...", "..."],
          "전문_기술": ["...", "..."],
          "지원_이유": "...",
          ...기타 발견한 키포인트...
        }}
        ```
        
        반드시 JSON 형식으로만 출력하고, JSON 외의 메시지는 포함하지 마세요.
        사용자 스토리에서 발견할 수 있는 모든 관련 정보를 자유롭게 구조화하세요.
        """
        
        groq_logger.debug(f"키포인트 추출 프롬프트 길이: {len(keypoints_prompt)}")
        
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b")
        keypoints_response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 텍스트에서 핵심 정보를 주체적으로 파악하고 구조화하는 전문가입니다. 미리 정해진 형식에 얽매이지 않고 텍스트의 본질을 파악하세요."},
                {"role": "user", "content": keypoints_prompt}
            ],
            temperature=0.2  # 약간의 창의성을 허용하면서도 일관성 유지
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {keypoints_response.usage.total_tokens if hasattr(keypoints_response, 'usage') else 'N/A'}")
        
        # 응답 전체를 JSON으로 로깅
        try:
            response_json = {
                "id": keypoints_response.id,
                "model": keypoints_response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content
                        },
                        "finish_reason": choice.finish_reason
                    } for choice in keypoints_response.choices
                ],
                "usage": {
                    "prompt_tokens": keypoints_response.usage.prompt_tokens,
                    "completion_tokens": keypoints_response.usage.completion_tokens,
                    "total_tokens": keypoints_response.usage.total_tokens
                } if hasattr(keypoints_response, 'usage') else {}
            }
            groq_logger.info(f"키포인트 추출 API 응답 JSON: {json.dumps(response_json, ensure_ascii=False)}")
        except Exception as e:
            groq_logger.error(f"키포인트 응답 JSON 변환 오류: {str(e)}")
        
        if keypoints_response and hasattr(keypoints_response, 'choices') and len(keypoints_response.choices) > 0:
            json_output = keypoints_response.choices[0].message.content
            
            # JSON 문자열에서 코드 블록 표시 제거
            if "```json" in json_output or "```" in json_output:
                json_output = re.sub(r'```(?:json)?\n?', '', json_output)
                json_output = re.sub(r'```', '', json_output)
            
            # 출력이 실제 JSON인지 확인
            try:
                user_keypoints = json.loads(json_output.strip())
                groq_logger.info(f"사용자 스토리 키포인트 추출 성공: {list(user_keypoints.keys())}")
            except json.JSONDecodeError as e:
                error_msg = f"사용자 스토리 키포인트 JSON 파싱 오류: {str(e)}"
                logger.error(error_msg)
                groq_logger.error(error_msg)
                # 기본 구조로 대체
                user_keypoints = {
                    "핵심_강점": "",
                    "관련_경험": [],
                    "전문_기술": [],
                    "지원_이유": "",
                    "기타_특이사항": ""
                }
        else:
            error_msg = "사용자 스토리 키포인트 API 응답 오류"
            logger.error(error_msg)
            groq_logger.error(error_msg)
            user_keypoints = {
                "핵심_강점": "",
                "관련_경험": [],
                "전문_기술": [],
                "지원_이유": "",
                "기타_특이사항": ""
            }
    except Exception as e:
        error_msg = f"사용자 스토리 키포인트 추출 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        groq_logger.error(error_msg)
        groq_logger.debug(traceback.format_exc())
        user_keypoints = {
            "핵심_강점": "",
            "관련_경험": [],
            "전문_기술": [],
            "지원_이유": "",
            "기타_특이사항": ""
        }
    
    # 2단계: 추출된 키포인트를 이용해 자기소개서 생성
    # 사용자 정보 섹션 구성
    user_info_section = json.dumps(user_keypoints, ensure_ascii=False, indent=2)
    
    prompt = f"""
    다음 정보를 바탕으로 완성된 자기소개서를 작성해주세요:
    
    [채용공고]
    {job_description}
    
    [회사 정보]
    {company_info}
    
    [지원자 정보 (JSON)]
    {user_info_section}
    
    다음 사항을 포함하는 완성도 높은 자기소개서를 작성해주세요:
    1. 지원자의 핵심 경쟁력과 지원 동기
    2. 회사와 직무에 대한 이해도
    3. 입사 후 기여 방안
    4. 성과와 역량은 구체적 수치로 표현 (예: "생산성 30% 향상", "만족도 4.8/5 달성")
    5. 전문 용어와 업계 용어를 자연스럽게 사용하고 열정과 자신감을 표현하는 어조 사용
    6. 직무 관련 핵심 키워드를 3-5개 자연스럽게 강조
    7. 회사 문화와 가치관과 일치하는 내용 강조
    8. 지원자 정보에서 추출된 키포인트를 적절히 활용하여 개인 맞춤형 내용 구성
    """
    
    groq_logger.debug(f"생성된 통합 프롬프트 길이: {len(prompt)}")
    
    try:
        groq_logger.info(f"Groq API 호출 시작 - 모델: qwen-qwq-32b (자기소개서 생성)")
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 작성 전문가입니다. 채용공고와 회사 정보를 분석하여 지원자 정보를 바탕으로 완성도 높은 자기소개서를 작성해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        groq_logger.debug(f"Groq API 응답 수신 - 토큰 수: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
        # 응답 전체를 JSON으로 로깅
        try:
            response_json = {
                "id": response.id,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content[:500] + "..." if len(choice.message.content) > 500 else choice.message.content
                        },
                        "finish_reason": choice.finish_reason
                    } for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if hasattr(response, 'usage') else {}
            }
            groq_logger.info(f"자기소개서 생성 API 응답 JSON: {json.dumps(response_json, ensure_ascii=False)}")
        except Exception as e:
            groq_logger.error(f"자기소개서 응답 JSON 변환 오류: {str(e)}")
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            finalized_resume = response.choices[0].message.content
            
            # 출력 및 처리 과정 로깅
            additional_info = {
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None,
                "extracted_keypoints": list(user_keypoints.keys())
            }
            outputs = {
                "finalized_resume_length": len(finalized_resume),
                "finalized_resume": finalized_resume
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
