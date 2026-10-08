import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

for (const width of [1440, 390]) {
  test(`body measurements stay visible in the requested rows at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 });
    await page.goto('/');
    for (const tab of ['Key inputs', 'History']) {
      await page.getByRole('tab', { name: tab, exact: true }).click();
      await expect(page.locator('.fields-scroll input, .fields-scroll select').first()).toBeVisible();
      const names = await page.locator('.fields-scroll input, .fields-scroll select')
        .evaluateAll(inputs => inputs.slice(0, 5).map(input => input.getAttribute('aria-label')));
      expect(names).toEqual(['Age', 'Sex', 'Height', 'Weight', 'BMI']);
      const boxes = await Promise.all(['Age', 'Sex', 'Height', 'Weight'].map(name =>
        page.getByLabel(name, { exact: true }).boundingBox()));
      const [age, sex, height, weight] = boxes;
      expect(age && sex && height && weight).toBeTruthy();
      expect(Math.abs(age!.y - sex!.y)).toBeLessThan(2);
      expect(Math.abs(height!.y - weight!.y)).toBeLessThan(2);
      expect(height!.y).toBeGreaterThan(age!.y);
      expect(weight!.x).toBeGreaterThan(height!.x);
      await expect(page.getByLabel('Height', { exact: true })).toBeEditable();
      await expect(page.getByLabel('Weight', { exact: true })).toBeEditable();
      await expect(page.getByLabel('BMI', { exact: true })).not.toBeEditable();
    }
    await page.getByRole('tab', { name: 'Key inputs', exact: true }).click();
    await page.getByLabel('Height', { exact: true }).fill('172');
    await page.getByLabel('Weight', { exact: true }).fill('120');
    await expect(page.getByLabel('BMI', { exact: true })).toHaveValue('40.56');
    const outDir = path.resolve('../demo/screenshots');
    fs.mkdirSync(outDir, { recursive: true });
    await page.locator('.fields-scroll').evaluate(element => { element.scrollTop = 0; });
    await page.locator('.patient-panel').screenshot({ path: path.join(outDir, `bmi-inputs-${width}.png`) });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

    await page.getByLabel('Height', { exact: true }).fill('');
    await expect(page.getByLabel('BMI', { exact: true })).toHaveValue('');
    await expect(page.getByRole('button', { name: 'Predict coronary risk', exact: true })).toBeDisabled();
    await page.getByLabel('Height', { exact: true }).fill('0');
    await expect(page.getByRole('button', { name: 'Predict coronary risk', exact: true })).toBeDisabled();
    await page.getByRole('button', { name: 'Reset inputs', exact: true }).click();
    await expect(page.getByLabel('Height', { exact: true })).toHaveValue('164');
    await expect(page.getByLabel('Weight', { exact: true })).toHaveValue('54');
    await expect(page.getByLabel('BMI', { exact: true })).toHaveValue('20.08');
  });
}

test('import, real prediction and export use BMI calculated from height and weight', async ({ page, request }) => {
  await page.goto('/');
  const response = await request.get('/api/cases');
  expect(response.ok()).toBe(true);
  const { cases } = await response.json();
  const features = { ...cases[0].features, Length: 172, Weight: 120, BMI: 0 };
  await page.locator('input[type="file"]').setInputFiles({
    name: 'patient.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify({ features })),
  });
  await expect(page.getByLabel('BMI', { exact: true })).toHaveValue('40.56');
  const predictionRequest = page.waitForRequest(request => request.url().endsWith('/api/predict') && request.method() === 'POST');
  const predictionResponse = page.waitForResponse(response => response.url().endsWith('/api/predict') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Predict coronary risk', exact: true }).click();
  const sent = (await predictionRequest).postDataJSON();
  expect(sent.features.Length).toBe(172);
  expect(sent.features.Weight).toBe(120);
  expect(sent.features.BMI).toBeCloseTo(120 / 1.72 ** 2, 12);
  expect((await predictionResponse).ok()).toBe(true);
  const exportButton = page.getByRole('button', { name: 'Export case', exact: true });
  await expect(exportButton).toBeEnabled();
  const downloadPromise = page.waitForEvent('download');
  await exportButton.click();
  const download = await downloadPromise;
  const exported = JSON.parse(fs.readFileSync((await download.path())!, 'utf8'));
  expect(exported.features.BMI).toBe(sent.features.BMI);
});
