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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger('crawlers')
logger.debug(f"DEBUG: AZURE_VISION_KEY loaded as: {getattr(settings, 'AZURE_VISION_KEY', 'Not Set')}")
logger.debug(f"DEBUG: AZURE_VISION_ENDPOINT loaded as: {getattr(settings, 'AZURE_VISION_ENDPOINT', 'Not Set')}")

# OCR 전용 파일 핸들러 및 logger 추가
ocr_log_path = os.path.join('logs', 'crawling', 'ocr_debug.log')
ocr_file_handler = logging.FileHandler(ocr_log_path, encoding='utf-8')
ocr_file_handler.setLevel(logging.INFO)
ocr_file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s %(message)s'))
ocr_logger = logging.getLogger('ocr_debug')
ocr_logger.setLevel(logging.INFO)
if not any(isinstance(h, logging.FileHandler) and h.baseFilename == ocr_file_handler.baseFilename for h in ocr_logger.handlers):
    ocr_logger.addHandler(ocr_file_handler)

# Django 로깅 설정 사용
# logger = logging.getLogger('crawlers') # Removed duplicate logger initialization

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
        
        # 원본 HTML 저장 (근본 원인 진단용)
        try:
            with open('logs/crawling/job_post_raw.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            logger.error(f"원본 HTML 저장 실패: {e}")
        
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
            cleaned_text = f"{cleaned_text}{image_text}"
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
    """HTML에서 이미지를 추출하고 Azure Computer Vision OCR로 처리하여 텍스트 반환 (URL 방식)"""
    try:
        job_post_images = set()
        images = soup.find_all('img')
        for img in images:
            img_url = None
            # 1. srcset이 있으면 첫 번째 후보
            img_srcset = img.get('srcset', '')
            if img_srcset:
                src_candidates = [s.strip().split(' ')[0] for s in img_srcset.split(',') if s.strip()]
                if src_candidates:
                    img_url = src_candidates[0]
            # 2. src
            if not img_url:
                img_src = img.get('src', '')
                if img_src:
                    img_url = img_src
            # 3. data-src
            if not img_url:
                img_data_src = img.get('data-src', '')
                if img_data_src:
                    img_url = img_data_src
            # 4. data-original
            if not img_url:
                img_data_original = img.get('data-original', '')
                if img_data_original:
                    img_url = img_data_original
            # 절대경로 변환
            if img_url and not img_url.startswith(('http://', 'https://', 'data:')):
                from urllib.parse import urljoin
                img_url = urljoin(base_url, img_url)
            if img_url:
                job_post_images.add(img_url)
        job_post_images = list(job_post_images)
        logger.info(f"[IMG-DEBUG] 최종 OCR 대상 이미지 리스트: {job_post_images}")
        print(f"[IMG-DEBUG] 최종 OCR 대상 이미지 리스트: {job_post_images}")
        ocr_logger.info(f"[IMG-DEBUG] 최종 OCR 대상 이미지 리스트: {job_post_images}")
        if not job_post_images:
            logger.info(" 채용공고 관련 이미지를 찾을 수 없습니다.")
            print("[IMG-DEBUG] 채용공고 관련 이미지를 찾을 수 없습니다.")
            return ""
        logger.info(f" 총 {len(job_post_images)}개의 채용공고 관련 이미지를 찾았습니다.")
        print(f"[IMG-DEBUG] 총 {len(job_post_images)}개의 채용공고 관련 이미지를 찾았습니다.")
        ocr_results = []
        for img_url in job_post_images:
            try:
                logger.debug(f"[IMG-DEBUG] Azure OCR URL 방식 처리 시작: {img_url}")
                print(f"[IMG-DEBUG] Azure OCR URL 방식 처리 시작: {img_url}")
                ocr_logger.info(f"[IMG-DEBUG] Azure OCR URL 방식 처리 시작: {img_url}")
                ocr_text = call_azure_ocr_url(img_url)
                if ocr_text:
                    logger.debug(f"[IMG-DEBUG] OCR 결과 (일부): {ocr_text[:100]}...")
                    print(f"[IMG-DEBUG] OCR 결과 (일부): {ocr_text[:100]}...")
                    ocr_logger.info(f"[IMG-DEBUG] OCR 결과 (일부): {ocr_text[:100]}...")
                    ocr_results.append(ocr_text)
                else:
                    logger.debug(f"[IMG-DEBUG] OCR 결과 없음 또는 추출 실패: {img_url}")
                    print(f"[IMG-DEBUG] OCR 결과 없음 또는 추출 실패: {img_url}")
                    ocr_logger.info(f"[IMG-DEBUG] OCR 결과 없음 또는 추출 실패: {img_url}")
            except Exception as e:
                logger.error(f"[IMG-DEBUG] 이미지 URL OCR 처리 중 오류 발생 ({img_url}): {str(e)}", exc_info=settings.DEBUG)
                print(f"[IMG-DEBUG] 이미지 URL OCR 처리 중 오류 발생 ({img_url}): {str(e)}")
                ocr_logger.error(f"[IMG-DEBUG] 이미지 URL OCR 처리 중 오류 발생 ({img_url}): {str(e)}")
                continue
        all_ocr_text = "\n".join(ocr_results)
        if all_ocr_text:
            logger.debug("[IMG-DEBUG] 모든 이미지 OCR(URL) 처리 완료")
            print("[IMG-DEBUG] 모든 이미지 OCR(URL) 처리 완료")
            ocr_logger.info("[IMG-DEBUG] 모든 이미지 OCR(URL) 처리 완료")
        return all_ocr_text
    except Exception as e:
        logger.error(f"[IMG-DEBUG] [이미지 URL OCR 전체 오류]: {str(e)}", exc_info=settings.DEBUG)
        print(f"[IMG-DEBUG] [이미지 URL OCR 전체 오류]: {str(e)}")
        ocr_logger.error(f"[IMG-DEBUG] [이미지 URL OCR 전체 오류]: {str(e)}")
        return ""

def call_azure_ocr_url(image_url: str):
    """Azure Computer Vision API를 호출하여 이미지 URL에서 텍스트 추출"""
    try:
        AZURE_VISION_KEY = os.getenv('AZURE_VISION_KEY')
        AZURE_VISION_ENDPOINT = os.getenv('AZURE_VISION_ENDPOINT')
        ocr_url = f"{AZURE_VISION_ENDPOINT}/vision/v3.2/read/analyze"

        logger.info(f"[OCR-DEBUG] Vision API 요청 URL: {ocr_url}")
        logger.info(f"[OCR-DEBUG] Vision API KEY: {AZURE_VISION_KEY[:6]}... (생략)")
        print(f"[OCR-DEBUG] Vision API 요청 URL: {ocr_url}")
        print(f"[OCR-DEBUG] Vision API KEY: {AZURE_VISION_KEY[:6]}... (생략)")
        ocr_logger.info(f"[OCR-DEBUG] Vision API 요청 URL: {ocr_url}")
        ocr_logger.info(f"[OCR-DEBUG] Vision API KEY: {AZURE_VISION_KEY[:6]}... (생략)")

        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': AZURE_VISION_KEY
        }
        data = {"url": image_url}

        response = requests.post(ocr_url, headers=headers, json=data)
        logger.info(f"[OCR-DEBUG] Vision API 응답 status: {response.status_code}")
        print(f"[OCR-DEBUG] Vision API 응답 status: {response.status_code}")
        logger.info(f"[OCR-DEBUG] Vision API 응답 body: {response.text[:200]}")
        print(f"[OCR-DEBUG] Vision API 응답 body: {response.text[:200]}")
        ocr_logger.info(f"[OCR-DEBUG] Vision API 응답 status: {response.status_code}")
        ocr_logger.info(f"[OCR-DEBUG] Vision API 응답 body: {response.text[:200]}")
        response.raise_for_status()

        operation_url = response.headers["Operation-Location"]
        logger.info(f"[OCR-DEBUG] Operation-Location: {operation_url}")
        print(f"[OCR-DEBUG] Operation-Location: {operation_url}")
        ocr_logger.info(f"[OCR-DEBUG] Operation-Location: {operation_url}")

        result_headers = {'Ocp-Apim-Subscription-Key': AZURE_VISION_KEY}
        import time
        poll_count = 0
        max_polls = 10
        poll_delay = 1
        while poll_count < max_polls:
            result_response = requests.get(operation_url, headers=result_headers)
            logger.info(f"[OCR-DEBUG] Poll {poll_count} status: {result_response.status_code}")
            print(f"[OCR-DEBUG] Poll {poll_count} status: {result_response.status_code}")
            logger.info(f"[OCR-DEBUG] Poll {poll_count} body: {result_response.text[:200]}")
            print(f"[OCR-DEBUG] Poll {poll_count} body: {result_response.text[:200]}")
            ocr_logger.info(f"[OCR-DEBUG] Poll {poll_count} status: {result_response.status_code}")
            ocr_logger.info(f"[OCR-DEBUG] Poll {poll_count} body: {result_response.text[:200]}")
            result = result_response.json()
            if "status" in result and result["status"] == "succeeded":
                break
            time.sleep(poll_delay)
            poll_count += 1
        extracted_text = ""
        if "analyzeResult" in result and "readResults" in result["analyzeResult"]:
            for read_result in result["analyzeResult"]["readResults"]:
                for line in read_result["lines"]:
                    extracted_text += line["text"] + " "
        logger.info(f"[OCR-DEBUG] 최종 OCR 추출 텍스트: {extracted_text[:200]}")
        print(f"[OCR-DEBUG] 최종 OCR 추출 텍스트: {extracted_text[:200]}")
        ocr_logger.info(f"[OCR-DEBUG] 최종 OCR 추출 텍스트: {extracted_text[:200]}")
        return extracted_text.strip()
    except Exception as e:
        logger.error(f"[OCR-DEBUG] Azure Computer Vision OCR API(URL) 호출 실패: {str(e)}", exc_info=True)
        print(f"[OCR-DEBUG] Azure Computer Vision OCR API(URL) 호출 실패: {str(e)}")
        ocr_logger.error(f"[OCR-DEBUG] Azure Computer Vision OCR API(URL) 호출 실패: {str(e)}")
        return ""

# urlparse를 위한 함수 추가
def urljoin(base, url):
    """URL 결합 유틸리티 함수"""
    from urllib.parse import urljoin as urllib_urljoin
    return urllib_urljoin(base, url)

def save_html_with_selenium(url, out_path):
    """Selenium으로 렌더링된 HTML을 저장한다."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(5)  # JS 렌더링 대기
        html = driver.page_source
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
    finally:
        driver.quit()

def save_images_from_network_with_selenium(url, out_path):
    """Selenium + DevTools로 네트워크 패널 기반 이미지 URL을 추출한다."""
    user_agent = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/123.0.0.0 Safari/537.36'
    )
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument(f'user-agent={user_agent}')
    # 자동화 탐지 우회
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        driver.get(url)
        time.sleep(5)  # JS/이미지 로딩 대기
        # 네트워크 로그에서 이미지 요청만 추출
        logs = driver.get_log('performance')
        img_urls = set()
        for entry in logs:
            msg = json.loads(entry['message'])
            params = msg.get('message', {}).get('params', {})
            request = params.get('request', {})
            url_ = request.get('url', '')
            if re.search(r'\.(jpg|jpeg|png|gif|bmp|webp)(\?|$)', url_, re.IGNORECASE):
                img_urls.add(url_)
        # 중복 제거 후 저장
        with open(out_path, 'w', encoding='utf-8') as f:
            for u in sorted(img_urls):
                f.write(u + '\n')
    finally:
        driver.quit()
