import os
import pytest
import time
from playwright.async_api import async_playwright, expect

@pytest.mark.asyncio
async def test_resume_generation():
    """
    이력서 생성 프로세스를 테스트합니다.
    1. 메인 페이지 접속
    2. 공고 URL 입력
    3. 회사 URL 입력
    4. 사용자 스토리 입력
    5. 생성하기 버튼 클릭
    6. 로딩 상태 확인
    7. 3분 이내 결과 확인
    8. 결과 확인 (성공 또는 실패)
    """
    # 테스트 결과 저장을 위한 디렉토리 생성
    os.makedirs("test-logs/playwright/screenshots", exist_ok=True)

    # CI 환경 확인 - GitHub Actions에서는 CI=true 환경 변수가 설정됨
    is_ci = os.environ.get('CI') == 'true'

    async with async_playwright() as playwright:
        # CI 환경에서는 headless=True, 로컬에서는 headless=False
        browser = await playwright.chromium.launch(headless=is_ci)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. 메인 페이지 접속
            await page.goto("http://localhost:8000")
            await expect(page).to_have_title("CVFactory")

            # 2. 공고 URL 입력
            job_url = "https://www.jobkorea.co.kr/Recruit/GI_Read/46699223?Oem_Code=C1&logpath=1&stext=%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5&listno=1&sc=63"
            await page.fill("#job_url", job_url)

            # 3. 회사 URL 입력
            company_url = "https://deepinsight.ninehire.site/"
            await page.fill("#company_url", company_url)

            # 4. 사용자 스토리 입력
            user_story = "안녕하세요. 저는 윤수혁이고 AI 개발자입니다."
            await page.fill("#user_story", user_story)

            # 5. 생성하기 버튼 클릭
            await page.click("button:has-text('생성하기')")

            # 6. 로딩 상태 확인
            loading_overlay = page.locator("#loading-overlay:visible")
            await expect(loading_overlay).to_be_visible()
            
            # 로딩 텍스트 확인
            loading_texts = await page.locator("#loading-overlay p").all_text_contents()
            print(f"로딩 텍스트: {loading_texts}")
            assert "자기소개서를 생성하는 중입니다" in " ".join(loading_texts), f"예상 텍스트가 포함되지 않음: {loading_texts}"
            assert "최대 3분 정도 소요될 수 있습니다" in " ".join(loading_texts), f"예상 텍스트가 포함되지 않음: {loading_texts}"

            # 7. 3분 이내 결과 확인
            start_time = time.time()
            last_log_time = start_time
            MAX_WAIT_TIME = 180  # 3분 (초 단위)
            LOG_INTERVAL = 10  # 10초 간격으로 로그 출력

            while time.time() - start_time < MAX_WAIT_TIME:
                current_time = time.time()
                if current_time - last_log_time >= LOG_INTERVAL:
                    print(f"로딩 중... 경과 시간: {int(current_time - start_time)}초")
                    last_log_time = current_time
                
                # 로딩 오버레이의 가시성 체크
                is_visible = await loading_overlay.is_visible()
                if not is_visible:
                    print("로딩이 완료되었습니다.")
                    break
                
                await page.wait_for_timeout(10000)  # 10초 대기

            if time.time() - start_time >= MAX_WAIT_TIME:
                print("3분이 지났지만 로딩이 완료되지 않았습니다.")
                raise TimeoutError("로딩이 3분 이상 지속되었습니다.")

            # 8. 결과 확인
            result_text = await page.locator("#generated_resume").text_content()
            if not result_text or result_text.strip() == "":
                print("자기소개서 생성 실패: 결과가 비어있습니다.")
                raise AssertionError("자기소개서가 생성되지 않았습니다.")
            
            # 결과 길이 확인 (최소 100자 이상)
            if len(result_text.strip()) < 100:
                print(f"자기소개서 생성 실패: 결과가 너무 짧습니다. (길이: {len(result_text.strip())}자)")
                raise AssertionError("생성된 자기소개서가 너무 짧습니다.")
            
            print(f"자기소개서 생성 성공! (길이: {len(result_text.strip())}자)")

        except Exception as e:
            print(f"테스트 실패: {e}")
            raise
        finally:
            await browser.close() 