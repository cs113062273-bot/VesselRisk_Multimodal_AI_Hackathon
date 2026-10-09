import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

for (const width of [1280, 1440, 1920]) {
  test(`body measurements stay together in the horizontal patient profile at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto('/');
    await expect(page.locator('.patient-panel')).toBeVisible();
    const layout = await page.locator('.workspace').evaluate(workspace => {
      const patient = workspace.querySelector('.patient-panel')!.getBoundingClientRect();
      const viewer = workspace.querySelector('.anatomy-workspace')!.getBoundingClientRect();
      const explanation = workspace.querySelector('.explanation-panel')!.getBoundingClientRect();
      const fields = workspace.querySelector('.fields-scroll')!.getBoundingClientRect();
      return { patientBottom: patient.bottom, patientWidth: patient.width, workspaceWidth: workspace.clientWidth,
        viewerTop: viewer.top, viewerRight: viewer.right, explanationTop: explanation.top,
        explanationLeft: explanation.left, fieldsHeight: fields.height };
    });
    expect(layout.patientBottom).toBeLessThan(layout.viewerTop);
    expect(Math.abs(layout.viewerTop - layout.explanationTop)).toBeLessThan(2);
    expect(layout.viewerRight).toBeLessThan(layout.explanationLeft);
    expect(layout.patientWidth / layout.workspaceWidth).toBeGreaterThan(.9);
    expect(layout.fieldsHeight).toBeLessThan(400);
    await page.getByRole('tab', { name: 'Labs & echo', exact: true }).click();
    await page.evaluate(() => document.fonts.ready);
    const valve = await page.getByLabel('Valvular heart disease', { exact: true }).boundingBox();
    const predict = await page.getByRole('button', { name: 'Predict coronary risk', exact: true }).boundingBox();
    expect(Math.abs(valve!.y + valve!.height / 2 - predict!.y - predict!.height / 2)).toBeLessThan(2);
    expect(predict!.width).toBeLessThanOrEqual(250);
    expect(predict!.height).toBeGreaterThanOrEqual(50);
    await expect(page.getByText('Inputs changed · run to update all targets', { exact: true })).toHaveCount(0);
    await page.locator('.patient-panel').screenshot({ path: path.resolve(`../demo/screenshots/labs-inputs-${width}.png`) });
    for (const tab of ['Key inputs', 'History']) {
      await page.getByRole('tab', { name: tab, exact: true }).click();
      await expect(page.locator('.fields-scroll input, .fields-scroll select').first()).toBeVisible();
      const names = await page.locator('.fields-scroll input, .fields-scroll select')
        .evaluateAll(inputs => inputs.slice(0, 5).map(input => input.getAttribute('aria-label')));
      expect(names).toEqual(['Age', 'Sex', 'Height', 'Weight', 'BMI']);
      // Measure one layout frame; separate protocol calls can straddle font loading/reflow.
      await page.evaluate(() => document.fonts.ready);
      const boxes = await page.locator('.fields-scroll input, .fields-scroll select').evaluateAll(inputs =>
        inputs.slice(0, 4).map(input => { const r = input.getBoundingClientRect(); return { x: r.x, y: r.y }; }));
      const [age, sex, height, weight] = boxes;
      expect(age && sex && height && weight).toBeTruthy();
      expect(Math.abs(age!.y - sex!.y)).toBeLessThan(2);
      expect(Math.abs(height!.y - weight!.y)).toBeLessThan(2);
      expect(Math.abs(height!.y - age!.y)).toBeLessThan(2);
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
