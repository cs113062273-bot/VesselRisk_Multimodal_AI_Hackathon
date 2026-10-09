import { defineConfig } from '@playwright/test';

const baseURL = process.env.DEMO_URL || 'http://127.0.0.1:3000';
const apiPort = process.env.PLAYWRIGHT_API_PORT || '8000';
const python = process.env.PLAYWRIGHT_PYTHON || 'python';
const webPort = new URL(baseURL).port || '3000';
export default defineConfig({
  testDir: './e2e', timeout: 90000, expect: { timeout: 20000 }, workers: 1, reporter: 'list',
  webServer: process.env.CI ? [
    { command: `"${python}" -m uvicorn api.main:app --host 127.0.0.1 --port ${apiPort}`, cwd: '..', url: `http://127.0.0.1:${apiPort}/health`, timeout: 120000, reuseExistingServer: false },
    { command: `npm run start -- --port ${webPort}`, url: baseURL, timeout: 120000, reuseExistingServer: false, env: { API_URL: `http://127.0.0.1:${apiPort}` } },
  ] : undefined,
  use: { baseURL, viewport: { width: 1440, height: 1000 }, launchOptions: { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] }, screenshot: 'only-on-failure', trace: 'retain-on-failure' },
});
