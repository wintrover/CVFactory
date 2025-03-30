import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import pandas as pd
import logging
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # 로그 형식
    handlers=[
        logging.StreamHandler()  # 콘솔에 로그 출력
    ]
)

logger = logging.getLogger(__name__)  # 현재 모듈(__name__)에 대한 로거 생성

# ------------------------------
# 1. 설정 (키워드 & 깊이 & 필터링)
# ------------------------------
max_depth = 2  # 크롤링 깊이 2로 제한
visited_urls = set()  # 방문한 URL 저장

# 크롤링 제외할 URL 패턴
EXCLUDE_URLS = [
    "login", "signin", "signup", "register", "user", "account", "profile",
    "password", "mypage", "session", "search", "apply", "cart", "recruit",
    "faq", "help", "terms", "privacy", "support", "subsid", "policy",
    "guide", "myform", "email", "phoneBook", "process", "return",
    "로그인", "회원가입", "비밀번호", "계정", "아이디", "고객센터",
    "문의", "이용약관", "개인정보처리방침", "약관", "법적고지", "자주 묻는 질문",
    "도움말", "지원하기", "채용 공고", "채용 절차", "이메일 문의",
    "채용 FAQ", "온라인 문의", "자주 하는 질문", "연락처"
]

# 크롤링할 주요 URL 패턴
TARGET_KEYWORDS = [
    "about", "vision", "mission", "values", "culture", "philosophy",
    "our-story", "who-we-are", "strategy", "sustainability", "esg",
    "corporate", "ethics", "principles", "history", "leadership",
    "careers", "people", "insight", "story", "team", "life",
    "company", "identity", "responsibility", "commitment",
    "work", "growth", "innovation", "environment", "future",
    "비전", "미션", "핵심가치", "철학", "가치", "목표", "전략",
    "비전선언문", "기업소개", "윤리", "기업 윤리", "사회적 책임",
    "지속 가능성", "환경", "윤리 강령", "리더십", "성장", "혁신",
    "기업문화", "조직문화", "근무 환경", "일하는 방식", "기업가정신",
    "팀워크", "경영이념", "인재상", "핵심 인재", "조직문화",
    "채용 철학", "일하기 좋은 회사", "우리의 가치"
]

# 크롤링 후 제거할 단어 목록
EXCLUDE_WORDS = [
    "로그인", "아이디", "비밀번호", "회원가입", "검색", "채용공고",
    "지원하기", "인재 등록", "공고", "상시지원", "채용 안내"
]

# ------------------------------
# 3. Selenium 설정
# ------------------------------
def get_webdriver():
    """도커 환경에서도 작동하는 웹드라이버 인스턴스를 반환합니다"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # 도커 환경에서는 ChromeDriverManager 대신 직접 경로 지정
    if os.environ.get('SELENIUM_DRIVER_EXECUTABLE_PATH'):
        # 도커 환경
        service = Service(executable_path='/usr/bin/chromedriver')
        logger.info("도커 환경에서 Selenium 실행")
    else:
        # 로컬 환경
        service = Service(ChromeDriverManager().install())
        logger.info("로컬 환경에서 Selenium 실행")
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"웹드라이버 초기화 오류: {str(e)}")
        return None

# ------------------------------
# 4. 정적/동적 페이지 감지
# ------------------------------
def detect_page_type(url):
    """ 페이지 유형 감지: 정적(static) 또는 동적(dynamic) """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            html = response.text
            if html.count("<script") > 5:
                return "dynamic"
            return "static"
    except requests.exceptions.RequestException:
        return "dynamic"
    return "static"

# ------------------------------
# 5. 불필요한 문장 제거
# ------------------------------
def clean_text(text):
    """ 불필요한 문구 제거 및 정제 """
    return "\n".join([line.strip() for line in text.split("\n") if len(line.strip()) > 20])

# ------------------------------
# 6. 정적 페이지 크롤링
# ------------------------------
def crawl_static(url):
    """ 정적 페이지에서 텍스트 추출 """
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return clean_text(text)
    except requests.exceptions.RequestException:
        return ""

# ------------------------------
# 7. 동적 페이지 크롤링
# ------------------------------
def crawl_dynamic(url):
    """ 동적 페이지에서 Selenium을 사용하여 텍스트 추출 """
    driver = get_webdriver()
    if not driver:
        logger.error("웹드라이버 초기화 실패로 크롤링을 진행할 수 없습니다.")
        return ""
    
    try:
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return clean_text(text)
    except Exception as e:
        logger.error(f"동적 페이지 크롤링 중 오류 발생: {str(e)}")
        return ""
    finally:
        driver.quit()

# ------------------------------
# 8. 회사 정보 크롤링 개선 함수 (Company_Crawler 통합)
# ------------------------------
def crawl_enhanced(start_url):
    """ Company_Crawler 방식으로 개선된 크롤링 함수 """
    driver = get_webdriver()
    if not driver:
        logger.error("웹드라이버 초기화 실패로 크롤링을 진행할 수 없습니다.")
        return ""
    
    try:
        # 1차 크롤링: 시작 URL
        logger.info(f"1차 크롤링: {start_url}")
        driver.get(start_url)
        
        # 텍스트 추출
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        main_text = soup.get_text(separator=" ", strip=True)
        
        # 링크 추출
        elements = driver.find_elements(By.TAG_NAME, "a")
        all_links = [elem.get_attribute("href") for elem in elements if elem.get_attribute("href")]
        
        # 같은 도메인 링크만 필터링
        base_domain = urlparse(start_url).netloc
        valid_links = []
        for link in all_links:
            if link and link.startswith('http'):
                link_domain = urlparse(link).netloc
                if link_domain == base_domain:
                    # TARGET_KEYWORDS와 일치하는 링크를 우선적으로 선택
                    for keyword in TARGET_KEYWORDS:
                        if keyword in link.lower():
                            valid_links.append(link)
                            break
        
        # 중복 제거
        links = list(dict.fromkeys(valid_links))
        
        # 최대 5개 링크만 선택 (TARGET_KEYWORDS 포함된 링크 우선)
        links = links[:5]
        
        result_text = f"=== 1차 크롤링: {start_url} ===\n{main_text}\n\n"
        
        # 2차 크롤링
        logger.info(f"2차 크롤링: {len(links)}개 링크")
        
        for i, link in enumerate(links):
            try:
                logger.info(f"링크 {i+1}/{len(links)}: {link}")
                driver.get(link)
                
                # 텍스트 추출
                soup = BeautifulSoup(driver.page_source, "html.parser")
                for script in soup(["script", "style"]):
                    script.extract()
                sub_text = soup.get_text(separator=" ", strip=True)
                
                # 결과 추가
                result_text += f"=== 2차 크롤링 ({i+1}/{len(links)}): {link} ===\n{sub_text}\n\n"
            
            except Exception as e:
                logger.error(f"오류 ({link}): {e}")
        
        logger.info("크롤링 완료")
        return result_text
        
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {str(e)}")
        return ""
    finally:
        driver.quit()

# ------------------------------
# 9. csrftoken과 sessionid 획득
# ------------------------------
def get_csrf_token_and_session_id():
    """ Selenium을 이용해 CSRF 토큰과 세션 ID를 가져오기 """
    driver = get_webdriver()
    if not driver:
        logger.error("웹드라이버 초기화 실패로 CSRF 토큰과 세션 ID를 가져올 수 없습니다.")
        return None, None
    
    try:
        logger.info("CSRF 토큰 및 세션 ID 가져오는 중...")
        
        driver.get("http://127.0.0.1:8000/")
        time.sleep(3)  # 페이지 로드 대기

        csrf_token = None
        session_id = None

        # 쿠키에서 CSRF 토큰과 세션 ID 가져오기
        for cookie in driver.get_cookies():
            if cookie["name"] == "csrftoken":
                csrf_token = cookie["value"]
            if cookie["name"] == "sessionid":
                session_id = cookie["value"]

        if not csrf_token or not session_id:
            logger.error("CSRF 토큰 또는 세션 ID를 가져오지 못했습니다.")
            return None, None

        logger.info(f"CSRF 토큰: {csrf_token}")
        logger.info(f"세션 ID: {session_id}")

        return csrf_token, session_id
    except Exception as e:
        logger.error(f"CSRF 토큰 및 세션 ID 가져오기 실패: {str(e)}")
        return None, None
    finally:
        driver.quit()

# ------------------------------
# 10. 크롤링 실행 - 개선된 버전
# ------------------------------
def fetch_company_info(company_url):
    """ 회사 정보를 크롤링하는 함수 """
    try:
        logger.info(f" 회사 정보 크롤링 시작: {company_url}")

        # URL 검증
        if not company_url.startswith('http://') and not company_url.startswith('https://'):
            company_url = 'https://' + company_url
            logger.info(f"URL 수정됨: {company_url}")

        # 크롤링 방식 선택: 향상된 버전 사용
        company_info = crawl_enhanced(company_url)
        
        if not company_info:
            logger.warning("향상된 크롤링 방식이 실패했습니다. 기존 방식으로 시도합니다.")
            # 기존 방식으로 시도
            page_type = detect_page_type(company_url)
            if page_type == "static":
                company_info = crawl_static(company_url)
            else:
                company_info = crawl_dynamic(company_url)

        logger.info(f"크롤링 완료, 총 {len(company_info)} 자 수집됨")
        
        # 결과 반환
        return company_info

    except Exception as e:
        logger.error(f"회사 정보 크롤링 중 오류 발생: {str(e)}")
        return "회사 정보를 가져오는 중에 오류가 발생했습니다. 다시 시도해주세요."

# 테스트 코드
if __name__ == "__main__":
    # 테스트용 회사 URL
    test_url = "https://www.samsung.com/"
    result = fetch_company_info(test_url)
    print(f"크롤링 결과 길이: {len(result)}")
    print(result[:500] + "...")  # 결과 앞부분만 출력
