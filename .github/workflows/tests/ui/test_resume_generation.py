import pytest
from playwright.sync_api import Page, expect

# Django 테스트 설정을 위한 데코레이터
pytestmark = pytest.mark.django_db

def test_home_page_loads(page: Page):
    """홈페이지가 정상적으로 로드되는지 테스트합니다."""
    # 홈페이지로 이동
    page.goto('http://localhost:8000/')
    
    # 페이지 제목 확인
    assert page.title() != ""
    
    # 스크린샷 캡처
    page.screenshot(path="test-logs/playwright/screenshots/homepage.png")
    
    print("홈페이지 로드 테스트 완료")

def test_resume_form_exists(page: Page):
    """이력서 생성 폼이 존재하는지 테스트합니다."""
    # 홈페이지로 이동
    page.goto('http://localhost:8000/')
    
    # 폼 요소 확인 (가정: 폼이 존재함)
    form = page.locator('form')
    expect(form).to_be_visible()
    
    print("이력서 폼 확인 테스트 완료")

def test_resume_preview_functionality(page: Page):
    """이력서 미리보기 기능이 동작하는지 테스트합니다."""
    # 이력서 생성 페이지로 이동 (가정: /resume/create 경로가 존재함)
    page.goto('http://localhost:8000/resume/create')
    
    # 필수 입력 필드 채우기 (가정: 이름과 이메일 필드가 존재함)
    page.fill('input[name="name"]', '홍길동')
    page.fill('input[name="email"]', 'test@example.com')
    
    # 미리보기 버튼 클릭 (가정: 미리보기 버튼이 존재함)
    page.click('button:has-text("미리보기")')
    
    # 미리보기 요소가 나타나는지 확인
    preview = page.locator('.resume-preview')
    expect(preview).to_be_visible()
    
    # 미리보기에 입력한 정보가 표시되는지 확인
    expect(page.locator('.resume-preview')).to_contain_text('홍길동')
    expect(page.locator('.resume-preview')).to_contain_text('test@example.com')
    
    # 스크린샷 캡처
    page.screenshot(path="test-logs/playwright/screenshots/resume-preview.png")
    
    print("이력서 미리보기 테스트 완료") 