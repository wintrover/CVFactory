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
        # 항상 headless=True로 설정 (CI 환경 구분 없이)
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 콘솔 로그 수집
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"BROWSER CONSOLE: {msg.text}"))
        
        # 네트워크 요청/응답 수집 (상세 로깅 강화)
        request_logs = []
        
        async def handle_request(req):
            # POST 요청인 경우 헤더와 본문 로깅
            if req.method == 'POST' and 'api' in req.url:
                headers = await req.all_headers()
                post_data = None
                try:
                    post_data = req.post_data
                except:
                    post_data = "로그 불가"
                
                log_msg = f"REQUEST: {req.method} {req.url}"
                if headers:
                    # API 키와 같은 민감 정보는 마스킹
                    if 'x-api-key' in headers:
                        headers['x-api-key'] = '****'
                    if 'authorization' in headers:
                        headers['authorization'] = '****'
                    log_msg += f", Headers: {headers}"
                if post_data:
                    log_msg += f", Body: {post_data[:200]}..."
                
                request_logs.append(log_msg)
            else:
                request_logs.append(f"REQUEST: {req.method} {req.url}")
        
        async def handle_response(res):
            # API 응답인 경우 상태 코드와 본문 로깅
            if 'api' in res.url:
                status = res.status
                log_msg = f"RESPONSE: {status} {res.url}"
                
                # 모든 종류의 HTTP 에러 상태 코드 체크
                if status >= 400:
                    try:
                        body = await res.text()
                        log_msg += f", 응답 본문: {body[:500]}..."
                    except Exception as e:
                        log_msg += f", 응답 본문 확인 실패: {e}"
                
                request_logs.append(log_msg)
            else:
                request_logs.append(f"RESPONSE: {res.status} {res.url}")
        
        page.on("request", handle_request)
        page.on("response", handle_response)

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
            
            # 검증 실패 시 즉시 테스트 실패로 처리
            if "자기소개서를 생성하는 중입니다" not in " ".join(loading_texts):
                raise AssertionError(f"예상 텍스트가 포함되지 않음: {loading_texts}")
            
            if "최대 3분 정도 소요될 수 있습니다" not in " ".join(loading_texts):
                raise AssertionError(f"예상 텍스트가 포함되지 않음: {loading_texts}")

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
                # 타임아웃 시 실패 처리
                await page.screenshot(path="test-logs/playwright/screenshots/timeout_failure.png")
                raise TimeoutError("로딩이 3분 이상 지속되었습니다.")

            # 로딩 완료 후 textarea에 내용이 채워질 때까지 기다리기
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 로딩 완료됨. 이제 자기소개서 내용이 채워질 때까지 기다립니다.")
            
            # 폴링 방식으로 변경 (CSP 제한 우회)
            max_wait = 30  # 30초 대기
            check_interval = 5  # 5초마다 확인
            start_wait = time.time()
            has_content = False
            
            while time.time() - start_wait < max_wait:
                try:
                    # 간단한 속성 접근만 수행 (CSP 제한 우회)
                    # 복잡한 JavaScript 문장 대신 단순 속성 조회로 변경
                    value_exists = await page.evaluate("!!document.getElementById('generated_resume')")
                    
                    if value_exists:
                        # 값이 있는지 확인 (별도 호출)
                        value = await page.locator('#generated_resume').input_value()
                        value_length = len(value)
                        print(f"현재 textarea 내용 길이: {value_length}자")
                        
                        if value_length > 0:
                            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 자기소개서 내용이 확인됨 (길이: {value_length}자)")
                            # 내용 미리보기
                            print(f"내용 미리보기: {value[:50]}..." if value_length > 50 else f"내용: {value}")
                            has_content = True
                            break
                    else:
                        print("textarea 요소를 찾을 수 없음")
                        # 요소를 찾지 못하는 경우 즉시 실패 처리
                        raise Exception("textarea 요소(#generated_resume)를 찾을 수 없습니다.")
                        
                except Exception as e:
                    print(f"값 확인 중 오류: {e}")
                    # 모든 예외를 테스트 실패로 처리
                    raise Exception(f"값 확인 중 오류가 발생했습니다: {e}")
                
                # 짧은 대기 후 다시 시도
                print(f"내용 확인 중... (경과: {int(time.time() - start_wait)}초)")
                await page.wait_for_timeout(check_interval * 1000)
            
            if not has_content:
                print(f"자기소개서 내용 확인 타임아웃: {max_wait}초 내에 내용이 채워지지 않음")
                
                # 스크린샷 저장
                await page.screenshot(path="test-logs/playwright/screenshots/waiting_timeout.png")
                print("스크린샷 저장됨: test-logs/playwright/screenshots/waiting_timeout.png")
                
                # DOM 상태 확인 및 저장
                html_content = await page.content()
                with open("test-logs/playwright/dom_state.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("DOM 상태 저장됨: test-logs/playwright/dom_state.html")
                
                # API 상태를 로그에 기록
                try:
                    response_logs = [log for log in request_logs if "RESPONSE:" in log and "/api/create_resume/" in log]
                    if response_logs:
                        print("API 응답 기록:")
                        for log in response_logs:
                            print(f"  {log}")
                    
                    # 모든 HTTP 에러 코드 확인 (400 이상)
                    error_logs = [log for log in response_logs if any(f"RESPONSE: {status}" in log for status in range(400, 600))]
                    if error_logs:
                        print("\n서버 에러가 발견되었습니다. 가능한 원인:")
                        print("1. API 키 설정 오류 - CI 환경에서 API 키가 올바르게 설정되었는지 확인")
                        print("2. 서버측 예외 - Django 로그에서 자세한 오류 확인 필요")
                        print("3. 환경 변수 문제 - CI 환경과 로컬 환경의 차이 확인")
                        print("\n에러 로그:")
                        for log in error_logs:
                            print(f"  {log}")
                        
                        # 테스트 실패 처리
                        raise Exception(f"서버에서 HTTP 에러가 발생했습니다: {error_logs[0]}. 테스트를 실패로 처리합니다.")
                
                except Exception as e:
                    print(f"API 로그 확인 중 오류: {e}")
                    # 예외 다시 발생시켜 테스트 실패 처리
                    raise
                
                # 테스트 실패 처리 (자기소개서 내용이 생성되지 않음)
                raise Exception("자기소개서가 생성되지 않았습니다. 테스트를 실패로 처리합니다.")

            # 8. 결과 확인 (내용이 없어도 계속 진행)
            result_element = page.locator('#generated_resume')
            is_visible = await result_element.is_visible()
            print(f"#generated_resume 요소 가시성: {is_visible}")
            
            try:
                # 값 가져오기 시도
                result_text = await result_element.input_value()
                result_length = len(result_text)
                
                if result_length > 0:
                    print(f"자기소개서 생성 성공! (길이: {result_length}자)")
                    print(f"자기소개서 시작 부분: {result_text[:100]}...")
                else:
                    print("자기소개서 내용이 비어 있습니다.")
                    # 자기소개서가 비어있는 경우도 테스트 실패 처리
                    raise Exception("자기소개서 내용이 비어 있습니다. 테스트를 실패로 처리합니다.")
            except Exception as e:
                print(f"결과 확인 중 오류: {e}")
                # 오류 발생 시 테스트 실패 처리
                raise Exception(f"결과 확인 중 오류가 발생했습니다: {e}. 테스트를 실패로 처리합니다.")

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