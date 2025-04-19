import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

async def crawl_page(url, browser=None, context=None, headless=True, timeout=15000):
    '''
    단일 페이지 크롤링 + 네트워크 감지 + 위장
    '''
    close_browser = False
    if browser is None:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        close_browser = True
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    locale = "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    if context is None:
        context = await browser.new_context(
            user_agent=user_agent,
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            extra_http_headers={"Accept-Language": locale},
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
    network_log = []
    page.on("request", lambda req: network_log.append({"type": "request", "url": req.url, "method": req.method, "headers": dict(req.headers)}))
    page.on("response", lambda res: network_log.append({"type": "response", "url": res.url, "status": res.status, "headers": dict(res.headers), "content_type": res.headers.get('content-type', '')}))
    await page.goto(url, timeout=timeout)
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    # 내부 링크 추출 (같은 도메인만)
    base = urlparse(url)
    internal_links = set()
    for a in soup.find_all("a", href=True):
        link = urljoin(url, a['href'])
        if urlparse(link).netloc == base.netloc:
            internal_links.add(link.split('#')[0])
    result = {
        "url": url,
        "html": html,
        "internal_links": list(internal_links),
        "network_log": network_log
    }
    await page.close()
    if close_browser:
        await browser.close()
        await playwright.stop()
    return result

async def crawl_site_recursive(start_url, max_depth=2, visited=None, browser=None, context=None, headless=True, timeout=15000):
    '''
    기업사이트 재귀적 크롤링 (내부적으로 crawl_page 사용)
    '''
    if visited is None:
        visited = set()
    if start_url in visited or max_depth < 0:
        return []
    visited.add(start_url)
    result = await crawl_page(start_url, browser=browser, context=context, headless=headless, timeout=timeout)
    results = [result]
    for link in result["internal_links"]:
        if link not in visited:
            results.extend(await crawl_site_recursive(link, max_depth-1, visited, browser, context, headless, timeout))
    return results 