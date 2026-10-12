import { test, expect } from '@playwright/test';
import path from 'node:path';
import fs from 'node:fs';
import { NAMES } from '../lib/types';

test('orbit starts on opening and successful predictions, stops on selection and stays stopped on return', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Pause', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('canvas')).toBeVisible();
  await expect(page.locator('.prediction-status')).toHaveCount(0);
  await page.getByRole('combobox', { name: 'View prediction target' }).selectOption('LAD');
  await expect(page.getByRole('button', { name: 'Orbit', exact: true })).toHaveAttribute('aria-pressed', 'false');
  for (const target of ['CAD', 'LCX', 'RCA', 'LAD']) {
    await page.getByRole('combobox', { name: 'View prediction target' }).selectOption(target);
    await expect(page.getByRole('button', { name: 'Orbit', exact: true })).toHaveAttribute('aria-pressed', 'false');
  }
  const predict = async () => {
    const response = page.waitForResponse(r => r.url().endsWith('/api/predict') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Predict coronary risk', exact: true }).click();
    expect((await response).ok()).toBe(true);
    await expect(page.getByRole('button', { name: 'Pause', exact: true })).toHaveAttribute('aria-pressed', 'true');
  };
  await predict();
  await expect(page.getByRole('button', { name: 'Pause', exact: true })).toBeVisible();
  await page.locator('.explanation-panel').getByRole('tab', { name: 'RCA', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Orbit', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Expand patient profile' }).click();
  await predict();
  await page.getByRole('button', { name: 'Model evidence', exact: true }).click();
  await page.getByRole('button', { name: 'Patient workspace', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Orbit', exact: true })).toHaveAttribute('aria-pressed', 'false');
  await page.getByRole('button', { name: 'Reset', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Orbit', exact: true })).toBeVisible();
});

test('artery navigation, readable explanations and updated predictions', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  const predict = async () => {
    const response = page.waitForResponse(r => r.url().endsWith('/api/predict') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Predict coronary risk', exact: true }).click();
    const result = await response;
    expect(result.ok()).toBe(true);
    await expect(page.getByRole('button', { name: 'Export case', exact: true })).toBeEnabled();
    return result.json();
  };
  const initial = await predict();
  const explanation = page.locator('.explanation-panel');
  for (const t of ['CAD', 'LAD', 'LCX', 'RCA']) await expect(explanation.getByRole('tab', { name: t, exact: true }).locator('strong')).toHaveText(`${(initial.targets[t].probability * 100).toFixed(1)}%`);
  for (const vessel of ['LAD', 'LCX', 'RCA']) await expect(page.getByRole('button', { name: `Select ${vessel} in 3D` })).toContainText(`${(initial.targets[vessel].probability * 100).toFixed(1)}%`);
  await expect(page.locator('[data-change-pp]')).toHaveCount(0);
  await expect(explanation.locator('.contribution-row').first()).toContainText('Yes');
  await expect(page.locator('.model-details')).not.toHaveAttribute('open');
  await page.getByText('All 55 inputs & calculation details', { exact: true }).click();
  await expect(page.locator('.model-facts')).toContainText('Sigmoid');
  await page.getByText('All 55 inputs & calculation details', { exact: true }).click();

  const out = path.resolve('../demo/screenshots');
  fs.mkdirSync(out, { recursive: true });
  const label = page.getByRole('button', { name: 'Select LCX in 3D' });
  const before = await label.boundingBox();
  for (const vessel of ['LCX', 'RCA', 'LAD'] as const) {
    await page.getByRole('combobox', { name: 'View prediction target' }).selectOption(vessel);
    await expect(page.locator('.view-caption')).toHaveText('Drag to rotate · Scroll to zoom · Click a vessel');
    await expect(explanation.locator('.target-name')).toHaveText(NAMES[vessel]);
    await expect(page.getByRole('button', { name: `Select ${vessel} in 3D` })).toHaveAttribute('aria-pressed', 'true');
    // Allow the actual camera transition to settle before reviewing its rendered view.
    await page.waitForTimeout(1500);
    if (vessel === 'LCX') {
      const after = await label.boundingBox();
      expect(Math.hypot(after!.x - before!.x, after!.y - before!.y)).toBeGreaterThan(20);
    }
    await page.locator('.heart-viewer').screenshot({ path: path.join(out, `focused-${vessel.toLowerCase()}.png`) });
  }
  await page.getByRole('combobox', { name: 'View prediction target' }).selectOption('CAD');
  await expect(explanation.getByRole('tab', { name: 'CAD', exact: true })).toHaveAttribute('aria-selected', 'true');
  await expect(page.locator('.view-caption')).toHaveText('Drag to rotate · Scroll to zoom · Click a vessel');
  await expect(page.locator('.projected-label[aria-pressed="true"]')).toHaveCount(0);
  await page.getByRole('button', { name: 'Expand patient profile' }).click();
  await page.getByLabel('Age', { exact: true }).fill('85');
  const updated = await predict();
  for (const vessel of ['LAD', 'LCX', 'RCA']) {
    const change = (updated.targets[vessel].probability - initial.targets[vessel].probability) * 100;
    if (Math.abs(change) >= .05) await expect(page.getByRole('button', { name: `Select ${vessel} in 3D` }).locator('[data-change-pp]')).toHaveAttribute('data-change-pp', change.toFixed(1));
  }
  for (const vessel of ['LAD', 'LCX', 'RCA']) {
    await explanation.getByRole('tab', { name: vessel, exact: true }).click();
    await page.getByRole('button', { name: 'Expand anatomy' }).click();
    await expect(page.locator('.selected-vessel-summary > strong')).toHaveText(`${(updated.targets[vessel].probability * 100).toFixed(1)}%`);
    if (vessel === 'RCA') await page.locator('.heart-viewer').screenshot({ path: path.join(out, 'prediction-changes.png') });
    await page.keyboard.press('Escape');
  }
  await page.getByRole('button', { name: 'Reset', exact: true }).click();
  await expect(page.locator('.view-caption')).toHaveText('Drag to rotate · Scroll to zoom · Click a vessel');
  await page.locator('.explanation-panel').getByRole('tab', { name: 'LCX', exact: true }).click();
  await expect(page.locator('.view-caption')).toHaveText('Drag to rotate · Scroll to zoom · Click a vessel');
  await page.waitForTimeout(1500);
  const stationary = await label.boundingBox();
  await page.getByRole('button', { name: 'Orbit', exact: true }).click();
  await expect.poll(async () => {
    const moving = await label.boundingBox();
    return Math.hypot(moving!.x - stationary!.x, moving!.y - stationary!.y);
  }).toBeGreaterThan(5);
  // Selecting from the explanation tabs also stops orbit and brings that artery into view.
  await explanation.getByRole('tab', { name: 'RCA', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Orbit', exact: true })).toBeVisible();
  await expect(page.locator('.view-caption')).toHaveText('Drag to rotate · Scroll to zoom · Click a vessel');
  await page.getByRole('button', { name: 'Expand anatomy' }).click();
  await expect(page.locator('.heart-viewer')).toHaveClass(/viewer-full/);
  await page.keyboard.press('Escape');
  await expect(page.locator('.heart-viewer')).not.toHaveClass(/viewer-full/);

  expect(errors).toEqual([]);
});
