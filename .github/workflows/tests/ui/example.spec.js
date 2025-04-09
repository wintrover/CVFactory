// example.spec.js
const { test, expect } = require('@playwright/test');

test.describe('기본 UI 테스트', () => {
  test('홈페이지가 로드되는지 확인', async ({ page }) => {
    // 홈페이지로 이동
    await page.goto('/');
    
    // 제목이 존재하는지 확인
    const title = await page.title();
    expect(title).toBeTruthy();
    
    // 로그 출력
    console.log(`페이지 제목: ${title}`);
    
    // 스크린샷 캡처
    await page.screenshot({ path: 'homepage.png' });
  });

  test('메인 네비게이션이 표시되는지 확인', async ({ page }) => {
    await page.goto('/');
    
    // 네비게이션 요소 확인
    const nav = await page.$('nav');
    expect(nav).not.toBeNull();
    
    // 로그 출력
    console.log('네비게이션 요소가 확인되었습니다.');
  });
}); 