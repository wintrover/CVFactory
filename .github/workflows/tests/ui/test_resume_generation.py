import pytest
import asyncio
from playwright.async_api import async_playwright, Page, expect
import time
import os
from asgiref.sync import sync_to_async

# 비동기 테스트로 변경
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
            
            # 6. 로딩 상태 확인 - visible 선택자 사용
            # 로딩 오버레이가 보이는지 확인
            loading_overlay = page.locator("#loading-overlay:visible")
            await expect(loading_overlay).to_be_visible()
            
            # 로딩 텍스트 확인
            loading_texts = await page.locator("#loading-overlay p").all_text_contents()
            print(f"로딩 텍스트: {loading_texts}")
            assert "자기소개서를 생성하는 중입니다" in " ".join(loading_texts), f"예상 텍스트가 포함되지 않음: {loading_texts}"
            assert "최대 3분 정도 소요될 수 있습니다" in " ".join(loading_texts), f"예상 텍스트가 포함되지 않음: {loading_texts}"
            
            # 7. 3분 이내 결과 확인
            start_time = time.time()
            loading_ended = False
            MAX_WAIT_TIME = 180  # 3분 (초 단위)
            
            while time.time() - start_time < MAX_WAIT_TIME:
                # 로딩 오버레이의 display 속성이 none인지 확인
                is_hidden = await loading_overlay.evaluate("el => window.getComputedStyle(el).display === 'none'")
                if is_hidden:
                    loading_ended = True
                    break
                await asyncio.sleep(1)
            
            # 8. 결과 확인 - 로딩이 3분 내에 끝났는지 확인
            if not loading_ended:
                print("\n=== 테스트 결과 ===")
                print(f"공고 URL: {job_url}")
                print(f"회사 URL: {company_url}")
                print(f"사용자 스토리: {user_story}")
                print("결과: 실패 - 3분 이내에 자기소개서 생성이 완료되지 않았습니다.")
                await page.screenshot(path="test-logs/playwright/screenshots/resume_generation_timeout.png")
                # 테스트를 실패로 처리
                assert False, "자기소개서 생성이 3분 이내에 완료되지 않았습니다"
            
            # 로딩이 끝났으면 결과 확인
            print("\n=== 테스트 결과 ===")
            print(f"공고 URL: {job_url}")
            print(f"회사 URL: {company_url}")
            print(f"사용자 스토리: {user_story}")
            
            # textarea에서 내용 확인 (id 선택자 사용)
            textarea_locator = page.locator("#generated_resume")
            await expect(textarea_locator).to_be_visible()
            
            # textarea의 값 가져오기
            textarea_value = await textarea_locator.input_value()
            textarea_empty = textarea_value == "" or textarea_value is None
            
            if textarea_empty:
                # 실패 메시지 확인 - 실패 메시지가 표시될 수 있는 다양한 방식 고려
                error_message = await page.evaluate("""() => {
                    // DOM에서 '자기소개서 생성에 실패했습니다' 텍스트를 포함하는 요소 찾기
                    const elements = Array.from(document.querySelectorAll('*'));
                    for (const el of elements) {
                        if (el.textContent && el.textContent.includes('자기소개서 생성에 실패했습니다')) {
                            return el.textContent.trim();
                        }
                    }
                    return null;
                }""")
                
                if error_message:
                    print(f"결과: 실패 - {error_message}")
                    await page.screenshot(path="test-logs/playwright/screenshots/resume_generation_failed.png")
                else:
                    print("결과: 빈 자기소개서 (생성 실패 또는 진행 중)")
                    await page.screenshot(path="test-logs/playwright/screenshots/resume_generation_empty.png")
            else:
                # 성공 - 텍스트 영역에 내용이 있음
                print("결과: 이력서 생성 성공!")
                print(f"생성된 자기소개서 내용 (처음 100자):\n{textarea_value[:100]}...")
                await page.screenshot(path="test-logs/playwright/screenshots/resume_generation_success.png")
            
        except Exception as e:
            # 실패 시 스크린샷 저장 및 디버깅 정보 추가
            await page.screenshot(path="test-logs/playwright/screenshots/resume_generation_exception.png")
            print(f"\n테스트 실패: {str(e)}")
            
            # 디버깅을 위한 HTML 덤프
            html_content = await page.content()
            with open("test-logs/playwright/debug_html.html", "w", encoding="utf-8") as f:
                f.write(html_content)
                
            raise
            
        finally:
            await context.close()
            await browser.close() 