import { test, expect } from '@playwright/test';
import type { Prediction } from '../lib/types';

test('patient explanations update by target while model evidence stays independent', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  const explanation = page.locator('.explanation-panel');
  await expect(explanation.getByText('Start with a patient.', { exact: true })).toBeVisible();
  await expect(page.locator('circle[data-predicted]')).toHaveCount(0);
  const response = page.waitForResponse(r => r.url().endsWith('/api/predict') && r.request().method() === 'POST', { timeout: 85000 });
  await page.getByRole('button', { name: 'Predict coronary risk', exact: true }).click();
  const prediction: Prediction = await (await response).json();
  await expect(page.getByRole('button', { name: 'Export case', exact: true })).toBeEnabled();
  await expect(page.getByRole('button', { name: 'Expand patient profile' })).toHaveAttribute('aria-expanded', 'false');
  for (const width of [1280, 1440, 1920]) {
    await page.setViewportSize({ width, height: 1000 });
    const regions = page.locator('.workspace-results > *');
    await expect(regions).toHaveCount(2);
    expect(await page.locator('.workspace-results').evaluate(el => el.scrollWidth <= el.clientWidth)).toBe(true);
    const chart = page.getByRole('region', { name: 'Patient model comparison' });
    const chartBox = await chart.boundingBox();
    const svgBox = await chart.locator('svg[role="img"]').boundingBox();
    expect(svgBox!.x + svgBox!.width).toBeLessThanOrEqual(chartBox!.x + chartBox!.width + 1);
  }
  for (const target of ['CAD', 'LAD', 'RCA', 'LCX'] as const) {
    await explanation.getByRole('tab', { name: target, exact: true }).click();
    await expect(page.getByRole('combobox', { name: 'View prediction target' })).toHaveValue(target);
    const risk = prediction.targets[target];
    const chart = page.getByRole('region', { name: 'Patient model comparison' });
    for (const model of risk.agreement) {
      const bar = chart.locator(`[data-model="${model.family}"]`);
      expect(Number(await bar.getAttribute('data-probability'))).toBeCloseTo(model.probability, 12);
      await expect(bar).toHaveAttribute('data-selected', String(model.family === risk.family));
    }
    await expect(explanation.locator('.patient-reason')).toContainText(`${(risk.explanation.base_probability*100).toFixed(1)}%`);
    await expect(explanation.locator('.model-details')).not.toHaveAttribute('open');
  }
  await explanation.getByText('All 55 inputs & calculation details', { exact: true }).click();
  await expect(explanation.locator('.model-details .contribution-row')).toHaveCount(55);
  await explanation.getByText('All 55 inputs & calculation details', { exact: true }).click();
  await page.getByRole('button', { name: 'Model evidence', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Model evidence', exact: true })).toBeVisible();
  const original = await page.getByRole('region', { name: 'All target validation results' }).innerText();
  await expect(page.locator('[data-evidence-target]')).toHaveCount(4);
  await expect(page.locator('.patient-contributions')).toHaveCount(0);
  await page.getByRole('button', { name: 'View RCA performance', exact: true }).click();
  await expect(page.getByRole('tab', { name: 'RCA', exact: true })).toHaveAttribute('aria-selected', 'true');
  await page.getByRole('button', { name: 'Patient workspace', exact: true }).click();
  await expect(page.getByRole('combobox', { name: 'View prediction target' })).toHaveValue('LCX');
  await expect(page.getByRole('button', { name: 'Orbit', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Expand patient profile' }).click();
  await page.getByLabel('Age', { exact: true }).fill('85');
  await expect(page.getByText('Previous explanation', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Model evidence', exact: true }).click();
  await expect(page.getByRole('region', { name: 'All target validation results' })).toHaveText(original, { useInnerText: true });
  for (const section of ['Validation', 'Interpretability', 'Robustness', 'Data & provenance']) {
    await page.getByRole('tab', { name: section, exact: true }).click();
    expect(await page.locator('.evidence-lab').evaluate(el => el.scrollWidth <= el.clientWidth)).toBe(true);
  }
  expect(errors).toEqual([]);
});
