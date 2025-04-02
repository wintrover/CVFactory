import os
from dotenv import load_dotenv
import groq
import re
import logging

# 로거 설정
logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

# .env 파일 로드
load_dotenv(dotenv_path="groq.env")

# Groq API 키 설정
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Groq API Key가 설정되지 않았습니다.")

# Groq 클라이언트 초기화
client = groq.Client(api_key=api_key)

def analyze_job_description(job_description):
    """
    1단계-1: 채용공고 분석
    """
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
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 채용공고 분석 전문가입니다. 주어진 채용공고의 주요 내용을 분석해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            job_analysis = response.choices[0].message.content
            logger.info(f"채용공고 분석 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            return job_analysis
        else:
            logger.error(f"채용공고 분석 API 응답 형식 오류: {response}")
            return "채용공고 분석 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"채용공고 분석 API 호출 오류: {str(e)}", exc_info=True)
        return "채용공고 분석 중 오류가 발생했습니다."

def analyze_company_info(company_info):
    """
    1단계-2: 회사 정보 분석
    """
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
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 회사 분석 전문가입니다. 주어진 회사 정보의 주요 내용을 분석해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            company_analysis = response.choices[0].message.content
            logger.info(f"회사 정보 분석 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            return company_analysis
        else:
            logger.error(f"회사 정보 분석 API 응답 형식 오류: {response}")
            return "회사 정보 분석 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"회사 정보 분석 API 호출 오류: {str(e)}", exc_info=True)
        return "회사 정보 분석 중 오류가 발생했습니다."

def analyze_job_and_company(job_description, company_info):
    """
    1단계: 채용공고와 회사 정보 분석
    """
    try:
        # 1단계-1: 채용공고 분석
        logger.debug("1단계-1: 채용공고 분석 시작")
        job_analysis = analyze_job_description(job_description)
        logger.debug(f"채용공고 분석: {job_analysis[:100]}...")
        
        # 1단계-2: 회사 정보 분석
        logger.debug("1단계-2: 회사 정보 분석 시작")
        company_analysis = analyze_company_info(company_info)
        logger.debug(f"회사 정보 분석: {company_analysis[:100]}...")
        
        # 분석 결과 통합
        analysis = f"""
        [채용공고 분석]
        {job_analysis}
        
        [회사 정보 분석]
        {company_analysis}
        """
        
        return analysis
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"채용공고/회사 분석 중 오류 발생: {error_msg}", exc_info=True)
        return "채용공고/회사 분석 중 오류가 발생했습니다."

def extract_job_keypoints(job_description):
    """
    채용공고에서 핵심 내용만 추출
    """
    try:
        logger.debug(f"=== extract_job_keypoints 시작 ===")
        logger.debug(f"입력 job_description 길이: {len(job_description)}")
        
        prompt = f"""다음 채용공고에서 핵심 내용만 추출해주세요:

채용공고:
{job_description}

다음 형식으로 추출해주세요:
1. 주요 업무 (3-4줄)
2. 필수 자격요건 (3-4줄)
3. 우대사항 (2-3줄)"""

        logger.debug(f"프롬프트 길이: {len(prompt)}")
        
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        logger.debug(f"응답 토큰 수: {response.usage.completion_tokens}")
        logger.debug(f"=== extract_job_keypoints 완료 ===")
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"extract_job_keypoints 오류: {str(e)}")
        raise

def create_resume_draft(job_keypoints, company_info, user_story):
    """
    2단계: 자기소개서 초안 작성
    """
    # 성장과정과 학교생활 제거
    filtered_story = {
        '성격의 장단점': user_story.get('성격의 장단점', ''),
        '지원 동기': user_story.get('지원 동기', ''),
        '입사 후 포부': user_story.get('입사 후 포부', '')
    }
    
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
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 작성 전문가입니다. 주어진 정보를 바탕으로 설득력 있는 자기소개서를 작성해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            draft = response.choices[0].message.content
            logger.info(f"자기소개서 초안 작성 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            return draft
        else:
            logger.error(f"자기소개서 초안 작성 API 응답 형식 오류: {response}")
            return "자기소개서 초안 작성 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"자기소개서 초안 작성 API 호출 오류: {str(e)}", exc_info=True)
        return "자기소개서 초안 작성 중 오류가 발생했습니다."

def finalize_resume_metrics(resume_draft):
    """
    3단계-1: 성과와 역량을 구체적 수치로 표현
    """
    prompt = f"""
    다음 자기소개서 초안의 성과와 역량을 구체적 수치로 표현해주세요:
    
    초안: {resume_draft}
    
    다음 사항을 개선해주세요:
    1. 모든 성과와 역량은 구체적 수치로 표현 (예: "생산성 30% 향상", "만족도 4.8/5 달성")
    2. 입사 시 예상 기여도를 수치로 제시 (예: "비용 40% 절감", "매출 15% 성장 기여")
    """
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 편집 전문가입니다. 주어진 초안의 성과와 역량을 구체적 수치로 표현해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            metrics = response.choices[0].message.content
            logger.info(f"자기소개서 수치화 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            return metrics
        else:
            logger.error(f"수치화 API 응답 형식 오류: {response}")
            return "자기소개서 수치화 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"수치화 API 호출 오류: {str(e)}", exc_info=True)
        return "자기소개서 수치화 중 오류가 발생했습니다."

def finalize_resume_style(resume_draft):
    """
    3단계-2: 문장 스타일 개선
    """
    prompt = f"""
    다음 자기소개서 초안의 문장 스타일을 개선해주세요:
    
    초안: {resume_draft}
    
    다음 사항을 개선해주세요:
    1. 전체 내용을 일관성 있게 다듬기
    2. 문법과 표현을 자연스럽게 개선
    """
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 편집 전문가입니다. 주어진 초안의 문장 스타일을 개선해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            style = response.choices[0].message.content
            logger.info(f"자기소개서 스타일 개선 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            return style
        else:
            logger.error(f"스타일 개선 API 응답 형식 오류: {response}")
            return "자기소개서 스타일 개선 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"스타일 개선 API 호출 오류: {str(e)}", exc_info=True)
        return "자기소개서 스타일 개선 중 오류가 발생했습니다."

def finalize_resume_emphasis(resume_draft):
    """
    3단계-3: 핵심 내용 강조
    """
    prompt = f"""
    다음 자기소개서 초안의 핵심 내용을 강조해주세요:
    
    초안: {resume_draft}
    
    다음 사항을 개선해주세요:
    1. 핵심 경쟁력과 지원 동기를 강조
    """
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": "당신은 자기소개서 편집 전문가입니다. 주어진 초안의 핵심 내용을 강조해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            emphasis = response.choices[0].message.content
            logger.info(f"자기소개서 핵심 강조 API 호출 성공 - 사용 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            return emphasis
        else:
            logger.error(f"핵심 강조 API 응답 형식 오류: {response}")
            return "자기소개서 핵심 강조 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"핵심 강조 API 호출 오류: {str(e)}", exc_info=True)
        return "자기소개서 핵심 강조 중 오류가 발생했습니다."

def finalize_resume(resume_draft):
    """
    3단계: 자기소개서 초안을 다듬고 최종본 작성
    """
    try:
        # 3단계-1: 성과와 역량을 구체적 수치로 표현
        logger.debug("3단계-1: 자기소개서 수치화 시작")
        metrics = finalize_resume_metrics(resume_draft)
        logger.debug(f"자기소개서 수치화: {metrics[:100]}...")
        
        # 3단계-2: 문장 스타일 개선
        logger.debug("3단계-2: 자기소개서 스타일 개선 시작")
        style = finalize_resume_style(metrics)
        logger.debug(f"자기소개서 스타일 개선: {style[:100]}...")
        
        # 3단계-3: 핵심 내용 강조
        logger.debug("3단계-3: 자기소개서 핵심 강조 시작")
        emphasis = finalize_resume_emphasis(style)
        logger.debug(f"자기소개서 핵심 강조: {emphasis[:100]}...")
        
        # 최종 자기소개서 완성
        final = emphasis
        
        # <think></think> 태그와 그 내용 제거
        final = re.sub(r'<think>.*?</think>', '', final, flags=re.DOTALL)
        
        return final
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"자기소개서 최종 작성 중 오류 발생: {error_msg}", exc_info=True)
        return "자기소개서 최종 작성 중 오류가 발생했습니다."

def generate_resume(job_description, company_info, user_story):
    """
    자기소개서 생성 메인 함수
    """
    try:
        # 1단계: 채용공고와 회사 정보 분석
        logger.debug("1단계: 채용공고/회사 분석 시작")
        job_keypoints = extract_job_keypoints(job_description)
        logger.debug(f"채용공고 핵심 추출: {job_keypoints[:100]}...")
        
        # 2단계: 자기소개서 초안 작성
        logger.debug("2단계: 자기소개서 초안 작성 시작")
        draft = create_resume_draft(job_keypoints, company_info, user_story)
        logger.debug(f"자기소개서 초안: {draft[:100]}...")
        
        # 3단계: 자기소개서 초안을 다듬고 최종본 작성
        logger.debug("3단계: 자기소개서 최종 작성 시작")
        final = finalize_resume(draft)
        logger.debug(f"자기소개서 최종본: {final[:100]}...")
        
        return final
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"자기소개서 생성 중 오류 발생: {error_msg}", exc_info=True)
        return "자기소개서 생성 중 오류가 발생했습니다."
