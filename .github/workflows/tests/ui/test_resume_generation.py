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
        
        # 콘솔 로그 수집
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"BROWSER CONSOLE: {msg.text}"))
        
        # 네트워크 요청/응답 수집
        request_logs = []
        page.on("request", lambda req: request_logs.append(f"REQUEST: {req.method} {req.url}"))
        page.on("response", lambda res: request_logs.append(f"RESPONSE: {res.status} {res.url}"))

        try:
            # 1. 메인 페이지 접속
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 테스트 시작: 메인 페이지 접속")
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
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 생성하기 버튼 클릭")
            await page.click("button:has-text('생성하기')")

            # 6. 로딩 상태 확인
            loading_overlay = page.locator("#loading-overlay:visible")
            await expect(loading_overlay).to_be_visible()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 로딩 오버레이 표시 확인됨")
            
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
                    # 추가 로그 - console_logs 최신 5개 출력
                    if console_logs:
                        print(f"최근 콘솔 로그 ({min(5, len(console_logs))}개):")
                        for log in console_logs[-5:]:
                            print(f"  {log}")
                    last_log_time = current_time
                
                # 로딩 오버레이의 가시성 체크
                is_visible = await loading_overlay.is_visible()
                if not is_visible:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 로딩이 완료되었습니다. 총 소요 시간: {int(time.time() - start_time)}초")
                    # 로딩 완료 시 스크린샷 저장
                    await page.screenshot(path="test-logs/playwright/screenshots/loading_complete.png")
                    print("로딩 완료 상태의 스크린샷이 저장되었습니다.")
                    break
                
                await page.wait_for_timeout(10000)  # 10초 대기

            if time.time() - start_time >= MAX_WAIT_TIME:
                print("3분이 지났지만 로딩이 완료되지 않았습니다.")
                raise TimeoutError("로딩이 3분 이상 지속되었습니다.")

            # 로딩 완료 후 textarea에 내용이 채워질 때까지 기다리기
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 로딩 완료됨. 이제 자기소개서 내용이 채워질 때까지 기다립니다.")
            
            try:
                # textarea 요소의 value가 비어있지 않을 때까지 기다리기 (최대 30초)
                print("textarea 내용 채워짐 기다리는 중...")
                await page.wait_for_function('''
                    document.getElementById('generated_resume') && 
                    document.getElementById('generated_resume').value && 
                    document.getElementById('generated_resume').value.length > 0
                ''', timeout=30000)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 자기소개서 내용이 채워짐 확인")
                
                # 추가적인 DOM 안정화를 위해 짧은 대기 (100ms)
                await page.wait_for_timeout(100)
            except Exception as e:
                print(f"자기소개서 내용 채워짐 기다리기 타임아웃: {e}")
                # 스크린샷 저장
                await page.screenshot(path="test-logs/playwright/screenshots/waiting_timeout.png")
                print("스크린샷 저장됨: test-logs/playwright/screenshots/waiting_timeout.png")
                
                # DOM 상태 확인 및 저장
                html_content = await page.content()
                with open("test-logs/playwright/dom_state.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("DOM 상태 저장됨: test-logs/playwright/dom_state.html")
                
                # textare 요소 값 직접 확인 시도
                try:
                    textarea_value = await page.evaluate('document.getElementById("generated_resume").value')
                    print(f"Textarea 값 직접 확인: 길이={len(textarea_value) if textarea_value else 0}")
                except Exception as inner_e:
                    print(f"Textarea 값 확인 실패: {inner_e}")
                
                raise
                
            # 8. 결과 확인
            # 요소 정보 로깅
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] #generated_resume 요소 확인 시작")
            result_element = page.locator("#generated_resume")
            
            # 요소 가시성 확인
            is_visible = await result_element.is_visible()
            print(f"#generated_resume 요소 가시성: {is_visible}")
            
            # 요소 값 확인
            try:
                # input_value() 메서드로 먼저 시도 (textarea는 value 속성을 가짐)
                result_text = await result_element.input_value()
                print(f"#generated_resume의 input_value 길이: {len(result_text)}")
            except Exception as e:
                print(f"input_value() 실패: {e}")
                # 실패 시 text_content() 메서드로 시도
                result_text = await result_element.text_content()
                print(f"#generated_resume의 text_content 길이: {len(result_text)}")
            
            # 콘솔에 저장된 모든 로그 출력
            print("\n=== 브라우저 콘솔 로그 (최대 10개) ===")
            for log in console_logs[-10:]:  # 최신 10개만 표시
                print(log)
            print("================================\n")
                
            if not result_text or result_text.strip() == "":
                # 결과가 비어있을 경우 추가 디버깅 정보 수집
                print("자기소개서 생성 실패: 결과가 비어있습니다.")
                # 페이지 전체 HTML 저장
                html_content = await page.content()
                debug_html_path = "test-logs/playwright/debug_page.html"
                os.makedirs(os.path.dirname(debug_html_path), exist_ok=True)
                with open(debug_html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"페이지 HTML이 {debug_html_path}에 저장되었습니다.")
                
                # 스크린샷 저장
                await page.screenshot(path="test-logs/playwright/screenshots/empty_result.png")
                print("빈 결과 상태의 스크린샷이 저장되었습니다.")
                
                raise AssertionError("자기소개서가 생성되지 않았습니다.")
            
            # 결과 길이 확인 (최소 100자 이상)
            if len(result_text.strip()) < 100:
                print(f"자기소개서 생성 실패: 결과가 너무 짧습니다. (길이: {len(result_text.strip())}자)")
                print(f"내용: {result_text}")
                raise AssertionError("생성된 자기소개서가 너무 짧습니다.")
            
            print(f"자기소개서 생성 성공! (길이: {len(result_text.strip())}자)")
            print(f"자기소개서 시작 부분: {result_text.strip()[:100]}...")

        except Exception as e:
            print(f"테스트 실패: {e}")
            # 실패 시 스크린샷
            await page.screenshot(path="test-logs/playwright/screenshots/test_failure.png")
            print("테스트 실패 상태의 스크린샷이 저장되었습니다.")
            raise
        finally:
            # 모든 로그 파일 저장
            if console_logs:
                os.makedirs("test-logs/playwright", exist_ok=True)
                with open("test-logs/playwright/console_logs.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(console_logs))
                print("콘솔 로그가 test-logs/playwright/console_logs.txt에 저장되었습니다.")
            
            if request_logs:
                os.makedirs("test-logs/playwright", exist_ok=True)
                with open("test-logs/playwright/network_logs.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(request_logs))
                print("네트워크 로그가 test-logs/playwright/network_logs.txt에 저장되었습니다.")
                
            await browser.close() 