import { test, expect } from '@playwright/test';
import path from 'node:path';

test('overview switches between ranking and detection, and selects matching evidence', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Evidence Lab', exact: true }).click();
  const overview = page.locator('.target-overview');
  const lcx = overview.getByRole('button', { name: 'Inspect LCX validation' });
  await expect(lcx).toContainText('0.728');
  await expect(lcx).toContainText('0.670–0.786');
  await lcx.click();
  await expect(page.getByRole('tab', { name: 'LCX', exact: true })).toHaveAttribute('aria-selected', 'true');
  await expect(page.locator('.auc-feature')).toContainText('0.728');
  await overview.screenshot({ path: path.resolve('../demo/screenshots/evidence-overview.png') });
  await overview.getByRole('button', { name: 'Recall at 0.50' }).click();
  await expect(lcx).toContainText('42.0%');
  await expect(lcx).toContainText('50 / 119 positives');
  await expect(overview.getByRole('button', { name: 'Inspect CAD validation' })).toContainText('92.1%');
  await expect(overview.locator('.overview-interval')).toHaveCount(0);
  await overview.getByRole('button', { name: 'ROC-AUC', exact: true }).click();
  await expect(overview.locator('.overview-interval')).toHaveCount(4);
});

test('threshold charts show both error costs from the frozen policy on desktop', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Evidence Lab', exact: true }).click();
  for (const [target, fn, fp, recall] of [['LCX', '19', '93', '84.0%'], ['RCA', '15', '101', '86.8%']]) {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.getByRole('tab', { name: target, exact: true }).click();
    const chart = page.getByLabel(`${target} threshold tradeoff`);
    await expect(chart.getByRole('region', { name: 'Missed positives', exact: true }).locator('.fixed b')).toHaveText('69');
    await expect(chart.getByRole('region', { name: 'Missed positives', exact: true }).locator('.selected b')).toHaveText(fn);
    await expect(chart.getByRole('region', { name: 'False positives', exact: true }).locator('.selected b')).toHaveText(fp);
    await expect(chart).toContainText(recall);
    const axes = await chart.locator('.tradeoff-axis').allTextContents();
    expect(axes[0]).toBe(axes[1]);
    await chart.screenshot({ path: path.resolve(`../demo/screenshots/evidence-thresholds-${target.toLowerCase()}.png`) });
  }
});
