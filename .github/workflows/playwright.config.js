// playwright.config.js
// 타입 체크 오류 방지를 위해 @ts-check 제거
const { defineConfig, devices } = require('@playwright/test');
const path = require('path');

// process 객체 타입 오류 방지 코드 수정
// process는 Node.js 전역 객체이므로 재정의하지 않음

module.exports = defineConfig({
  testDir: path.join(__dirname, 'tests/ui'),
  testMatch: ['**/*.spec.js', '**/*.spec.ts'],
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  // 타임아웃 설정
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],
  use: {
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
  ]
}); 