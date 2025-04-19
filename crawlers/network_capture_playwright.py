import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

LOG_PATH = Path('logs/crawling/network_capture.log')
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

async def capture_network(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        locale = "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        platform = "Win32"
        context = await browser.new_context(
            user_agent=user_agent,
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            extra_http_headers={
                "Accept-Language": locale
            },
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.0,
            is_mobile=False,
            has_touch=False,
            color_scheme="light"
        )
        page = await context.new_page()
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => false});"
            "Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});"
            "Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko', 'en-US', 'en']});"
        )

        async def log_request(request):
            entry = {
                'type': 'request',
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers),
                'post_data': request.post_data,
            }
            with LOG_PATH.open('a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        async def log_response(response):
            entry = {
                'type': 'response',
                'url': response.url,
                'status': response.status,
                'headers': dict(response.headers),
                'content_type': response.headers.get('content-type'),
            }
            with LOG_PATH.open('a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        page.on('request', log_request)
        page.on('response', log_response)

        await page.goto(url)
        await page.wait_for_timeout(5000)  # 5초 대기 (필요시 조정)
        await browser.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: python network_capture_playwright.py <URL>')
        exit(1)
    url = sys.argv[1]
    asyncio.run(capture_network(url)) 