import { expect, test } from '@playwright/test';
import type { Evidence } from '../lib/types';

test('calibration counts and local stability evidence follow the selected target', async ({ page, request }) => {
  const evidence: Evidence = await (await request.get('/api/evidence')).json();
  expect(evidence.reliability).toBeTruthy();
  await page.goto('/');
  await page.getByRole('button', { name: 'Model evidence', exact: true }).click();
  await page.getByRole('button', { name: 'View RCA performance', exact: true }).click();
  const calibration = page.locator('details').filter({ has: page.locator('summary', { hasText: 'Calibration evidence' }) });
  await calibration.locator('summary').click();
  await expect(calibration).toContainText('Training-prevalence baseline');
  for (const target of ['CAD', 'LAD', 'LCX', 'RCA'] as const) {
    await page.getByRole('tab', { name: target, exact: true }).click();
    const bins = evidence.reliability!.targets[target].probability.bins;
    expect(bins.reduce((sum, bin) => sum + bin.n, 0)).toBe(303);
    for (const bin of bins) await expect(calibration).toContainText(`${bin.positive} / ${bin.n}`);
  }
  const bins = evidence.reliability!.targets.RCA.probability.bins;
  await page.getByRole('tab', { name: 'Interpretability', exact: true }).click();
  const stability = page.locator('details').filter({ has: page.locator('summary', { hasText: 'Local explanation stability' }) });
  await stability.locator('summary').click();
  await expect(stability.locator('tbody tr')).toHaveCount(3);
  await expect(stability).toContainText('Different background vs 8-cycle reference');
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export evidence', exact: true }).click();
  const file = await (await download).createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of file!) chunks.push(Buffer.from(chunk));
  const exported = JSON.parse(Buffer.concat(chunks).toString());
  expect(exported.reliability.targets.RCA.probability.bins).toEqual(bins);
});

test('input provenance survives edits, reset, import and prediction export', async ({ page, request }) => {
  const { cases } = await (await request.get('/api/cases')).json();
  await page.goto('/');
  await expect(page.locator('.patient-input-scope')).toContainText('55 from cohort record');
  await page.getByLabel('Age', { exact: true }).fill('61');
  await expect(page.locator('.patient-input-scope')).toContainText('54 from cohort record · 1 user entered');
  await page.getByRole('button', { name: 'Reset inputs', exact: true }).click();
  await expect(page.locator('.patient-input-scope')).toContainText('55 from cohort record');
  await page.locator('input[type=file]').setInputFiles({ name: 'case.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify({ features: cases[0].features })) });
  await expect(page.locator('.patient-input-scope')).toContainText('54 imported · 1 calculated');
  await page.getByLabel('Weight', { exact: true }).fill('65');
  await expect(page.locator('.clinical-field').filter({ has: page.getByLabel('BMI', { exact: true }) })).toHaveAttribute('data-input-source', 'derived');
  const prediction = page.waitForResponse(response => response.url().endsWith('/api/predict') && response.request().method() === 'POST', { timeout: 85000 });
  await page.getByRole('button', { name: 'Predict coronary risk', exact: true }).click();
  expect((await prediction).ok()).toBe(true);
  await expect(page.getByRole('button', { name: 'Export case', exact: true })).toBeEnabled();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export case', exact: true }).click();
  const file = await (await download).createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of file!) chunks.push(Buffer.from(chunk));
  const exported = JSON.parse(Buffer.concat(chunks).toString());
  expect(exported.input_sources.Weight).toBe('entered');
  expect(exported.input_sources.BMI).toBe('derived');
  expect(exported.input_sources.Age).toBe('imported');
  expect(Object.keys(exported.input_sources)).toHaveLength(55);
  expect(exported.features.BMI).toBeCloseTo(65 / (cases[0].features.Length / 100) ** 2, 10);
  await page.getByRole('button', { name: 'Expand patient profile' }).click();
  await page.getByRole('button', { name: 'Reset inputs', exact: true }).click();
  await expect(page.locator('.patient-input-scope')).toContainText('54 cohort defaults');
  await expect(page.locator('.patient-input-scope')).toContainText('Review defaults before predicting.');
});
