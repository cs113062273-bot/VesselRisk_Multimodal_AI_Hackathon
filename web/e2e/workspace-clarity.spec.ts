import { test, expect } from '@playwright/test';

test('workspace and evidence share stable desktop header geometry and export location', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Predict coronary risk', exact: true })).toBeEnabled();
  await expect(page.getByText('Explore coronary risk.', { exact: true })).toHaveCount(0);
  await expect(page.getByText('Predict a patient profile. Select an artery. See what shaped its estimate.', { exact: true })).toHaveCount(0);
  const geometry = () => page.locator('.app-header').evaluate(header => {
    const box = (element: Element) => {
      const { x, y, width, height } = element.getBoundingClientRect();
      return { x, y, width, height };
    };
    return [header, header.querySelector('.brand')!, header.querySelector('nav')!,
      ...header.querySelectorAll('nav button'), header.querySelector('.header-export')!,
      header.querySelector('.icon-button')!].map(box);
  });
  for (const width of [1280, 1440, 1920]) {
    await page.setViewportSize({ width, height: 1000 });
    const workspace = await geometry();
    expect(workspace[0].height).toBe(76);
    await page.getByRole('button', { name: 'Model evidence', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Model evidence' })).toBeVisible();
    const evidence = await geometry();
    expect(evidence).toEqual(workspace);
    await expect(page.getByRole('button', { name: 'Export evidence', exact: true })).toHaveCount(1);
    await expect(page.locator('.app-header').getByRole('button', { name: 'Export evidence', exact: true })).toBeEnabled();
    await page.getByRole('button', { name: 'Patient workspace', exact: true }).click();
    expect(await geometry()).toEqual(workspace);
    await expect(page.locator('.app-header').getByRole('button', { name: 'Export case', exact: true })).toBeDisabled();
  }
  await page.getByRole('button', { name: 'Model evidence', exact: true }).click();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export evidence', exact: true }).click();
  expect((await download).suggestedFilename()).toBe('vesselrisk-evidence.json');
});

test('optional examples use patient descriptions and fill editable inputs', async ({ page, request }) => {
  await page.goto('/');
  const example = page.getByRole('combobox', { name: 'Example(Optional)', exact: true });
  await expect(example).toBeVisible();
  await expect(example.locator('option:enabled')).toHaveCount(8);
  await expect(example).not.toContainText('failure');
  await expect(example).not.toContainText('New profile');
  const { cases } = await (await request.get('/api/cases')).json();
  for (const patient of cases) {
    await example.selectOption(patient.id);
    await expect(page.getByLabel('Age', { exact: true })).toHaveValue(String(patient.features.Age));
    await expect(page.getByLabel('Sex', { exact: true })).toHaveValue(patient.features.Sex);
    await expect(page.getByLabel('Weight', { exact: true })).toHaveValue(String(patient.features.Weight));
    await expect(page.getByLabel('Age', { exact: true })).toBeEditable();
  }
  await page.getByLabel('Age', { exact: true }).fill('60');
  await page.getByRole('button', { name: 'Reset inputs', exact: true }).click();
  await expect(page.getByLabel('Age', { exact: true })).toHaveValue('59');
});

test('prediction feedback stays visible before the profile smoothly collapses', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.goto('/');
  const predict = page.getByRole('button', { name: 'Predict coronary risk', exact: true });
  await expect(predict).toBeEnabled();
  const motion = page.locator('#patient-profile-body').evaluate(async body => {
    const initialHeight = body.getBoundingClientRect().height;
    const start = performance.now();
    const heights: number[] = [];
    let busyAt = 0, collapsedAt = 0;
    while (performance.now() - start < 15000) {
      await new Promise<void>(resolve => requestAnimationFrame(() => resolve()));
      const now = performance.now();
      if (!busyAt && document.querySelector('.input-footer button[aria-busy="true"]')) busyAt = now;
      if (body.getAttribute('aria-hidden') === 'true') {
        if (!collapsedAt) collapsedAt = now;
        heights.push(body.getBoundingClientRect().height);
        if (getComputedStyle(body).visibility === 'hidden') {
          return { initialHeight, heights, feedbackMs: collapsedAt - busyAt, collapseMs: now - collapsedAt };
        }
      }
    }
    throw new Error('Patient profile did not finish collapsing');
  });
  await predict.click();
  await expect(page.getByRole('button', { name: 'Predicting…', exact: true })).toHaveAttribute('aria-busy', 'true');
  const frames = await motion;
  expect(frames.feedbackMs).toBeGreaterThanOrEqual(450);
  expect(frames.collapseMs).toBeGreaterThanOrEqual(450);
  expect(frames.heights.filter(height => height > 5 && height < frames.initialHeight - 5).length).toBeGreaterThan(5);
  expect(frames.heights.at(-1)).toBeLessThan(1);
  await expect(page.locator('#patient-profile-body')).toHaveAttribute('inert', '');
  await page.getByRole('button', { name: 'Expand patient profile' }).click();
  await expect(page.getByLabel('Age', { exact: true })).toHaveValue('54');
});

test('edited inputs keep explanations explicitly stale until the new response arrives', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('/');
  const predict = page.getByRole('button', { name: 'Predict coronary risk', exact: true });
  await predict.click();
  await expect(page.getByRole('button', { name: 'Export case', exact: true })).toBeEnabled();
  await page.locator('.explanation-panel').getByRole('tab', { name: 'LCX', exact: true }).click();
  const explanation = page.locator('.explanation-panel');
  const age = explanation.locator('.contribution-row').filter({ hasText: 'Age' });
  await expect(age).toContainText('54 years');
  await expect(page.getByRole('button', { name: 'Expand patient profile' })).toHaveAttribute('aria-expanded', 'false');
  await page.getByRole('button', { name: 'Expand patient profile' }).click();
  await page.getByLabel('Age', { exact: true }).fill('85');
  await expect(explanation.getByRole('status')).toContainText('Previous explanation');
  await expect(age).toContainText('54 years');
  await expect(page.getByRole('button', { name: 'Export case', exact: true })).toBeDisabled();
  // Release the response after inspecting the updating state, including page scrolling.
  let releaseResponse!: () => void;
  const responseGate = new Promise<void>(resolve => { releaseResponse = resolve; });
  await page.route('**/api/predict', async route => {
    const response = await route.fetch();
    await responseGate;
    await route.fulfill({ response });
  });
  await predict.click();
  await expect(explanation.getByRole('status')).toContainText('Updating explanation');
  await expect(page.locator('#patient-profile-body')).toBeVisible();
  releaseResponse();
  await expect(explanation.getByRole('status')).toHaveCount(0);
  await expect(page.locator('#patient-profile-body')).toBeHidden();
  await explanation.getByRole('button', { name: 'View all 55 contributions' }).click();
  await expect(age).toContainText('85 years');
  await page.getByRole('button', { name: 'Expand patient profile' }).click();
  await expect(page.getByLabel('Age', { exact: true })).toHaveValue('85');
  await page.locator('#demo-case').selectOption('41');
  await expect(explanation.getByRole('status')).toContainText('Previous explanation');
});

test('a failed prediction keeps patient inputs open for correction', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Age', { exact: true }).fill('60');
  await page.route('**/api/predict', route => route.fulfill({
    status: 503, contentType: 'application/json', body: JSON.stringify({ detail: 'Model service unavailable' }),
  }));
  await page.getByRole('button', { name: 'Predict coronary risk', exact: true }).click();
  await expect(page.locator('.error-banner[role="alert"]')).toContainText('Model service unavailable');
  await expect(page.locator('#patient-profile-body')).toBeVisible();
  await expect(page.getByLabel('Age', { exact: true })).toHaveValue('60');
  await expect(page.getByRole('button', { name: 'Collapse patient profile' })).toHaveAttribute('aria-expanded', 'true');
});

test('search finds measurements outside the current group and clearing restores that group', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('tab', { name: 'ECG', exact: true }).click();
  await page.getByLabel('Search clinical inputs').fill('cholesterol');
  await expect(page.getByLabel('LDL cholesterol', { exact: true })).toBeVisible();
  await expect(page.getByLabel('HDL cholesterol', { exact: true })).toBeVisible();
  await expect(page.locator('.field-group').first()).toHaveText('Laboratory & echo');
  await page.getByLabel('LDL cholesterol', { exact: true }).fill('110');
  await page.getByRole('button', { name: 'Clear search' }).click();
  await expect(page.getByRole('tab', { name: 'ECG', exact: true })).toHaveAttribute('aria-selected', 'true');
  await expect(page.getByLabel('Q Wave', { exact: true })).toBeVisible();
  await page.getByRole('tab', { name: 'Labs & echo', exact: true }).click();
  await expect(page.getByLabel('LDL cholesterol', { exact: true })).toHaveValue('110');
});
