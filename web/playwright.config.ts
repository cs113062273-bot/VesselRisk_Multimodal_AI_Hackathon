import { defineConfig } from '@playwright/test';
export default defineConfig({testDir:'./e2e',timeout:90000,expect:{timeout:20000},workers:1,reporter:'list',use:{baseURL:process.env.DEMO_URL||'http://127.0.0.1:3000',viewport:{width:1440,height:1000},launchOptions:{args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']},screenshot:'only-on-failure',trace:'retain-on-failure'}});
