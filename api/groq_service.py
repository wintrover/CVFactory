import os
from dotenv import load_dotenv
import groq
import re
import logging

# 로거 설정
logger = logging.getLogger("api")

# .env 파일 로드
load_dotenv(dotenv_path="groq.env")

# Groq API 키 설정
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Groq API Key가 설정되지 않았습니다.")

# Groq 클라이언트 초기화
client = groq.Client(api_key=api_key)

def generate_resume(job_description, user_story, company_info = ""):
    """
    Groq API를 호출하여 자기소개서를 생성하는 함수
    """
    prompt = f"""
    채용 공고 설명: {job_description}
    사용자의 이야기: {user_story}
    회사 정보: {company_info}

    위 정보를 바탕으로 다음 구조의 자기소개서를 작성하세요:

    1. 핵심역량과 지원동기 요약 (두괄식)
    2. 회사가 당면한 문제와 채용의 배경 분석
       - 현재 회사가 직면한 과제/문제점을 명확히 제시
       - 회사의 비전, 인재상과 대표자의 가치관을 분석에 반영
       - 이 문제를 해결하기 위해 지원자 같은 인재가 필요한 이유 설명
    3. 회사의 비전/인재상 분석 및 지원자 역량과의 연결성
       - 지원자의 역량이 회사의 비전과 인재상에 어떻게 부합하는지 설명
    4. 문제해결 능력과 관련 경험 (수치로 표현)
       - 유사한 문제를 해결했던 지원자의 구체적 경험 제시
       - 문제 해결 과정에서 활용한 접근법과 기술 설명
       - 지원자의 경험이 회사의 현재 문제 해결에 어떻게 적용될 수 있는지 상세히 설명
    5. 입사 후 기여 가능 분야 및 예상 성과 (수치로 제시)
       - 회사의 특정 문제에 대한 해결책 제안
       - 지원자의 역량이 실제 업무에 어떻게 적용될 수 있는지 구체적 방안
    6. 핵심 경쟁력 강조

    필수 반영사항:
    - 모든 성과와 역량은 구체적 수치로 표현 (예: "생산성 30% 향상", "만족도 4.8/5 달성")
    - 입사 시 예상 기여도를 수치로 제시 (예: "비용 40% 절감", "매출 15% 성장 기여")
    - 회사의 비전과 인재상에 맞춘 지원자의 강점 강조
    - 회사 당면 문제와 지원자 역량 간의 직접적 연결성 명시
    - 지원자의 경험이 회사의 현재 문제 해결에 어떻게 적용될 수 있는지 구체적인 사례와 함께 설명
    - 진정성 있는 내용으로 작성
    """

    try:
        # Groq API 호출
        response = client.chat.completions.create(
            model="qwen-qwq-32b",  # qwen-qwq-32b 모델 사용
            messages=[
                {"role": "system", "content": "당신은 자기소개서 전문가입니다. 주어진 채용 공고와 지원자 정보를 바탕으로 맞춤형 자기소개서를 작성해주세요. 회사의 비전과 인재상, 기업 문화를 반영한 내용을 포함하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000  # 출력 토큰 수 조정
        )
        
        # Groq API 응답 처리
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            generated_resume = response.choices[0].message.content
            
            # <think></think> 태그와 그 내용 제거
            generated_resume = re.sub(r'<think>.*?</think>', '', generated_resume, flags=re.DOTALL)
            
            logger.info("Groq API 호출 성공")
            logger.debug(f"생성된 자기소개서: {generated_resume[:100]}...")
            return generated_resume
        else:
            error_msg = f"Groq API 응답 형식 오류: {response}"
            logger.error(error_msg)
            return "자기소개서 생성 중 오류가 발생했습니다. 다시 시도해 주세요."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Groq API 호출 중 오류 발생: {error_msg}", exc_info=True)
        
        # 오류 유형에 따른 로깅
        if "413" in error_msg or "Request too large" in error_msg:
            logger.error(f"요청 크기 초과 오류: {error_msg}")
            return "자기소개서 생성 중 오류가 발생했습니다. 다시 시도해 주세요."
        elif "429" in error_msg:
            logger.error(f"요청 한도 초과 오류: {error_msg}")
            return "현재 서버가 혼잡합니다. 잠시 후 다시 시도해 주세요."
        else:
            logger.error(f"기타 API 오류: {error_msg}")
            return "자기소개서 생성 중 오류가 발생했습니다. 다시 시도해 주세요."
