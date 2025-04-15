import requests
from bs4 import BeautifulSoup
import logging
import re
import os
import io
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from django.conf import settings
from PIL import Image

# Django 로깅 설정 사용
logger = logging.getLogger('crawlers')

class WebScrapingError(Exception):
    """웹 스크래핑 관련 사용자 정의 예외"""
    pass

# 개발 환경에서 더 자세한 로깅을 위한 설정
def log_crawling_result(url, result):
    """크롤링 결과를 파일에 저장 (디버깅 용도)"""
    if not settings.DEBUG:
        return None
        
    log_dir = os.path.join("logs", "crawling")
    os.makedirs(log_dir, exist_ok=True)  # 로그 디렉토리 확인
    
    # 파일명 생성 (URL에서 일부 추출)
    domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
    domain_name = domain.group(1) if domain else "unknown"
    file_name = f"job_post_{domain_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_path = os.path.join(log_dir, file_name)
    
    # 결과 텍스트에 50글자마다 줄바꿈 추가
    formatted_result = format_text_by_line(result, line_length=50)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"URL: {url}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("="*80 + "\n")
        f.write(formatted_result)
        
    logger.debug(f"크롤링 결과를 파일에 저장: {file_path}")
    
    return file_path

def create_session():
    """ HTTP 요청 세션 생성 (재시도 설정 포함)"""
    session = requests.Session()
    retries = Retry(
        total=3,  # 최대 재시도 횟수
        backoff_factor=1,  # 재시도 간격
        status_forcelist=[429, 500, 502, 503, 504],  # 재시도할 HTTP 상태 코드
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_job_description(url: str) -> Optional[str]:
    """ 주어진 URL에서 채용 공고 정보를 크롤링하여 텍스트로 반환"""
    session = create_session()
    try:
        # 개발 환경에서 디버그 로깅
        if settings.DEBUG:
            logger.debug(f"채용 공고 크롤링 시작 (시간: {datetime.now().isoformat()}) - URL: {url}")
        else:
            logger.info(f"채용 공고 크롤링: {url}")

        #  HTTP 요청 헤더 설정 (User-Agent 지정)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        # response = requests.get(job_url, headers=headers, timeout=10)
 
        #  HTTP 요청 실행 (타임아웃 10초 설정)
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

        #  응답 인코딩 설정
        response.encoding = response.apparent_encoding or 'utf-8'
        html_content = response.text
        
        if settings.DEBUG:
            logger.debug(f" HTML 응답 데이터 수신 완료 - 길이: {len(html_content)} 바이트")
        else:
            logger.info(" HTML 응답 데이터 수신 완료")

        #  HTML 파싱
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 이미지 추출 및 OCR 처리
        image_text = extract_and_process_images(soup, url, session)
        
        raw_text = soup.get_text(separator='\n')
        logger.info(" HTML 파싱 및 텍스트 추출 완료")

        #  텍스트 정제
        cleaned_text = clean_text(raw_text)
        
        # 이미지에서 추출한 텍스트가 있으면 결합
        if image_text:
            cleaned_text = f"{cleaned_text}\n\n[이미지에서 추출한 텍스트]\n{image_text}"
            logger.info(" 이미지 OCR 텍스트 결합 완료")
        
        # 개발 환경에서만 결과 로깅
        if settings.DEBUG:
            log_crawling_result(url, cleaned_text)
            logger.debug(f" 텍스트 정제 완료 - 길이: {len(cleaned_text)} 자")
        else:
            logger.info(" 텍스트 정제 완료")

        return cleaned_text

    except requests.Timeout:
        logger.error(f" [시간 초과] {url} 요청이 너무 오래 걸림", exc_info=settings.DEBUG)
        raise WebScrapingError("시간 초과로 인해 요청이 실패했습니다.")

    except requests.ConnectionError:
        logger.error(f" [네트워크 오류] {url} 요청 실패 - 인터넷 연결 확인 필요", exc_info=settings.DEBUG)
        raise WebScrapingError("네트워크 연결 오류가 발생했습니다.")

    except requests.exceptions.RequestException as e:
        logger.error(f" [HTTP 요청 오류] {url} - {str(e)}", exc_info=settings.DEBUG)
        raise WebScrapingError(f"HTTP 요청 오류 발생: {str(e)}") from e

    except requests.exceptions.HTTPError as e:
        logger.error(f" [HTTP 오류] {url} - 상태 코드: {response.status_code}", exc_info=settings.DEBUG)
        raise WebScrapingError(f"HTTP 오류 발생: {response.status_code} - {response.reason}") from e

    except re.error as e:
        logger.error(f" [정규식 오류] 텍스트 정제 중 오류 발생 - {str(e)}", exc_info=settings.DEBUG)
        raise WebScrapingError(f"정규식 처리 오류 발생: {str(e)}") from e

    except AttributeError as e:
        logger.error(f" [HTML 파싱 오류] 필요한 요소를 찾을 수 없음 - {str(e)}", exc_info=settings.DEBUG)
        raise WebScrapingError("HTML 파싱 오류 발생: 필요한 요소를 찾을 수 없습니다") from e

    except Exception as e:
        logger.error(f" [예기치 않은 오류 발생] {str(e)}", exc_info=settings.DEBUG)
        raise WebScrapingError(f"예기치 않은 오류 발생: {str(e)}") from e

def clean_text(text: str) -> str:
    """ 크롤링된 텍스트에서 불필요한 문자를 제거하여 정제"""
    try:
        #  괄호와 그 안의 내용 제거
        text = re.sub(r'\(.*?\)', '', text)  # 소괄호 제거
        text = re.sub(r'\[.*?\]', '', text)  # 대괄호 제거

        #  연속된 공백 및 줄바꿈 정리
        text = re.sub(r'\s+', ' ', text).strip()

        #  유니코드 제어 문자 제거
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)

        return text
    except re.error as e:
        logger.error(f" [정규식 오류] 텍스트 정제 중 오류 발생 - {str(e)}")
        raise

def format_text_by_line(text: str, line_length: int = 50) -> str:
    """ 텍스트를 지정된 길이만큼 줄바꿈을 추가하여 가독성 개선"""
    try:
        #  50자마다 줄바꿈 추가
        lines = [text[i:i + line_length] for i in range(0, len(text), line_length)]
        formatted_text = "\n".join(lines)
        return formatted_text
    except Exception as e:
        logger.error(f" [텍스트 포맷팅 오류] - {str(e)}", exc_info=True)
        raise

def save_to_file(text: str, filename: str = "output.txt"):
    """ 정제된 텍스트를 파일로 저장 (50자마다 줄바꿈 추가)"""
    try:
        formatted_text = format_text_by_line(text, line_length=50)
        with open(filename, "w", encoding="utf-8") as file:
            file.write(formatted_text)
        logger.info(f" 결과가 파일에 저장됨: {filename}")
    except Exception as e:
        logger.error(f" [파일 저장 오류] {filename} 저장 실패 - {str(e)}", exc_info=True)

def extract_and_process_images(soup: BeautifulSoup, base_url: str, session) -> str:
    """HTML에서 이미지를 추출하고 Azure Computer Vision OCR로 처리하여 텍스트 반환"""
    try:
        # 채용공고와 관련된 이미지들 찾기 (특정 클래스나 ID를 가진 영역의 이미지)
        # 사이트마다 다른 구조를 가질 수 있으므로 일반적인 패턴으로 처리
        
        # 이미지 태그 중 채용정보를 담고 있을 가능성이 높은 이미지 필터링
        job_post_images = []
        
        # 일반적인 이미지 태그 찾기
        images = soup.find_all('img')
        for img in images:
            # 이미지 소스 URL 가져오기
            img_src = img.get('src', '')
            img_alt = img.get('alt', '').lower()
            img_class = img.get('class', [])
            
            # 채용공고 관련 이미지일 가능성이 높은 이미지 필터링
            # 클래스명이나, alt 텍스트에 '채용', '공고', '모집', 'job', 'recruit' 등의 키워드가 있는지 확인
            is_job_related = False
            job_keywords = ['채용', '공고', '모집', '자격', '우대', '경력', 'job', 'recruit', 'career']
            
            if any(keyword in img_alt for keyword in job_keywords):
                is_job_related = True
            
            if isinstance(img_class, list) and any(any(keyword in cls.lower() for keyword in job_keywords) for cls in img_class):
                is_job_related = True
                
            # 이미지 크기 속성이 있는 경우 확인 (작은 아이콘 제외)
            width = img.get('width', '')
            height = img.get('height', '')
            if width and height:
                try:
                    if int(width) > 200 and int(height) > 200:
                        is_job_related = True
                except ValueError:
                    pass
            
            # 상대 경로인 경우 절대 경로로 변환
            if img_src and not img_src.startswith(('http://', 'https://', 'data:')):
                img_src = urljoin(base_url, img_src)
                
            if img_src and is_job_related:
                job_post_images.append(img_src)
                
        # 이미지가 없으면 빈 문자열 반환
        if not job_post_images:
            logger.info(" 채용공고 관련 이미지를 찾을 수 없습니다.")
            return ""
            
        logger.info(f" 총 {len(job_post_images)}개의 채용공고 관련 이미지를 찾았습니다.")
        
        # 추출된 이미지들에서 OCR 처리
        ocr_results = []
        for img_url in job_post_images:
            try:
                # 이미지 다운로드
                img_response = session.get(img_url, timeout=10)
                img_response.raise_for_status()
                
                # Azure Computer Vision OCR API 호출
                ocr_text = call_azure_ocr(img_response.content)
                
                # 결과에 추가
                if ocr_text:
                    ocr_results.append(ocr_text)
                    logger.debug(f" 이미지에서 텍스트 추출 성공: {img_url[:50]}...")
            except Exception as e:
                logger.error(f" 이미지 OCR 처리 실패: {img_url[:50]}... - {str(e)}", exc_info=settings.DEBUG)
                continue
                
        # 결과 병합
        if ocr_results:
            return "\n\n".join(ocr_results)
        else:
            return ""
            
    except Exception as e:
        logger.error(f" 이미지 추출 및 OCR 처리 실패: {str(e)}", exc_info=settings.DEBUG)
        return ""

def call_azure_ocr(image_bytes):
    """Azure Computer Vision API를 호출하여 이미지에서 텍스트 추출"""
    try:
        # Azure Computer Vision API 설정
        subscription_key = settings.AZURE_VISION_KEY
        endpoint = settings.AZURE_VISION_ENDPOINT
        ocr_url = f"{endpoint}/vision/v3.2/read/analyze"
        
        # 요청 헤더 설정
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': subscription_key
        }
        
        # API 호출
        response = requests.post(ocr_url, headers=headers, data=image_bytes)
        response.raise_for_status()
        
        # 비동기 API이므로 작업 상태 확인을 위한 URL 가져오기
        operation_url = response.headers["Operation-Location"]
        
        # 결과 가져오기
        result_headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        
        # 작업 완료 대기 (최대 10초)
        import time
        poll_count = 0
        max_polls = 10
        poll_delay = 1  # 초 단위
        
        while poll_count < max_polls:
            result_response = requests.get(operation_url, headers=result_headers)
            result = result_response.json()
            
            if "status" in result and result["status"] == "succeeded":
                break
            
            time.sleep(poll_delay)
            poll_count += 1
        
        # 결과 처리
        extracted_text = ""
        if "analyzeResult" in result and "readResults" in result["analyzeResult"]:
            for read_result in result["analyzeResult"]["readResults"]:
                for line in read_result["lines"]:
                    extracted_text += line["text"] + " "
        
        return extracted_text.strip()
        
    except Exception as e:
        logger.error(f" Azure Computer Vision OCR API 호출 실패: {str(e)}", exc_info=settings.DEBUG)
        return ""

# urlparse를 위한 함수 추가
def urljoin(base, url):
    """URL 결합 유틸리티 함수"""
    from urllib.parse import urljoin as urllib_urljoin
    return urllib_urljoin(base, url)
