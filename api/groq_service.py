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

def analyze_job_and_company(job_description, company_info=""):
    """
    1단계: 채용 공고와 회사 정보 분석하는 함수
    """
    prompt = f"""
    다음 채용 공고와 회사 정보를 분석하여 핵심 요구사항과 회사 문화를 요약해주세요:
    
    채용 공고: {job_description}
    회사 정보: {company_info}
    
    다음 내용을 포함하여 분석해주세요:
    1. 회사가 필요로 하는 핵심 기술 및 역량
    2. 회사의 비전과 인재상
    3. 채용 포지션이 해결하려는 문제나 과제
    4. 이 직무에 지원자가 갖추어야 할 자질
    5. 회사의 업계 포지션과 주요 제품/서비스
    """
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 채용 분석 전문가입니다. 채용 공고와 회사 정보를 분석하여 핵심 요구사항을 추출하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            analysis = response.choices[0].message.content
            logger.info("채용 분석 API 호출 성공")
            return analysis
        else:
            logger.error(f"분석 API 응답 형식 오류: {response}")
            return "채용 정보 분석 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"분석 API 호출 오류: {str(e)}", exc_info=True)
        return "채용 정보 분석 중 오류가 발생했습니다."

def create_resume_draft(job_analysis, user_story):
    """
    2단계: 분석 결과와 사용자 정보를 바탕으로 자기소개서 초안 작성
    """
    prompt = f"""
    다음 채용 분석 정보와 사용자 이야기를 바탕으로 자기소개서 초안을 작성해주세요:
    
    채용 분석: {job_analysis}
    사용자 이야기: {user_story}
    
    다음 구조에 맞게 작성해주세요:
    1. 핵심역량과 지원동기 요약 (두괄식)
    2. 회사가 당면한 문제와 채용의 배경 분석
    3. 회사의 비전/인재상 분석 및 지원자 역량과의 연결성
    4. 문제해결 능력과 관련 경험
    5. 입사 후 기여 가능 분야
    """
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 작성 전문가입니다. 주어진 채용 분석과 사용자 정보를 바탕으로 맞춤형 자기소개서 초안을 작성해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            draft = response.choices[0].message.content
            logger.info("자기소개서 초안 API 호출 성공")
            return draft
        else:
            logger.error(f"초안 API 응답 형식 오류: {response}")
            return "자기소개서 초안 작성 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"초안 API 호출 오류: {str(e)}", exc_info=True)
        return "자기소개서 초안 작성 중 오류가 발생했습니다."

def finalize_resume(resume_draft):
    """
    3단계: 자기소개서 초안을 다듬고 최종본 작성
    """
    prompt = f"""
    다음 자기소개서 초안을 최종 완성해주세요:
    
    초안: {resume_draft}
    
    다음 사항을 개선해주세요:
    1. 모든 성과와 역량은 구체적 수치로 표현 (예: "생산성 30% 향상", "만족도 4.8/5 달성")
    2. 입사 시 예상 기여도를 수치로 제시 (예: "비용 40% 절감", "매출 15% 성장 기여")
    3. 전체 내용을 일관성 있게 다듬기
    4. 문법과 표현을 자연스럽게 개선
    5. 핵심 경쟁력과 지원 동기를 강조
    """
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 편집 전문가입니다. 주어진 초안을 더 설득력 있고 전문적으로 개선해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            final = response.choices[0].message.content
            # <think></think> 태그와 그 내용 제거
            final = re.sub(r'<think>.*?</think>', '', final, flags=re.DOTALL)
            logger.info("자기소개서 최종본 API 호출 성공")
            return final
        else:
            logger.error(f"최종본 API 응답 형식 오류: {response}")
            return "자기소개서 최종 작성 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"최종본 API 호출 오류: {str(e)}", exc_info=True)
        return "자기소개서 최종 작성 중 오류가 발생했습니다."

def generate_resume(job_description, user_story, company_info=""):
    """
    Groq API를 호출하여 자기소개서를 생성하는 함수
    """
    try:
        # 1단계: 채용 공고와 회사 정보 분석
        logger.debug("1단계: 채용 공고 및 회사 정보 분석 시작")
        job_analysis = analyze_job_and_company(job_description, company_info)
        logger.debug(f"채용 분석 결과: {job_analysis[:100]}...")
        
        # 2단계: 자기소개서 초안 작성
        logger.debug("2단계: 자기소개서 초안 작성 시작")
        resume_draft = create_resume_draft(job_analysis, user_story)
        logger.debug(f"자기소개서 초안: {resume_draft[:100]}...")
        
        # 3단계: 최종 자기소개서 완성
        logger.debug("3단계: 최종 자기소개서 작성 시작")
        final_resume = finalize_resume(resume_draft)
        logger.debug(f"최종 자기소개서: {final_resume[:100]}...")
        
        return final_resume
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"자기소개서 생성 과정 중 오류 발생: {error_msg}", exc_info=True)
        
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
