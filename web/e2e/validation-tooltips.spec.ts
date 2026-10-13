import { test, expect } from '@playwright/test';

test('validation curve points show values on hover and dismiss them on leave', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Model evidence', exact: true }).click();
  await page.getByRole('tab', { name: 'Validation', exact: true }).click();

  for (const target of ['CAD', 'LAD', 'LCX', 'RCA']) {
    await page.getByRole('tablist', { name: 'Evidence target' })
      .getByRole('tab', { name: target, exact: true }).click();

    for (const title of ['ROC curve', 'Precision–recall', 'Calibration curve']) {
      const section = page.locator('.curve-section').filter({
        has: page.getByRole('heading', { name: title, exact: true }),
      });
      await section.scrollIntoViewIfNeeded();
      const points = section.locator('.recharts-scatter-symbol circle[pointer-events="all"]');
      await expect(points.first()).toBeAttached();
      const point = points.nth(Math.floor(await points.count() / 2));
      // Hover the outer hit area, beyond the small visible dot.
      const box = await point.boundingBox();
      expect(box).not.toBeNull();
      await page.mouse.move(box!.x + box!.width / 2 + 5, box!.y + box!.height / 2);
      const tooltip = section.locator('.recharts-tooltip-wrapper');
      await expect(tooltip).toBeVisible();
      await expect(tooltip.locator('.recharts-tooltip-item-value').first()).toHaveText(/^\d+\.\d{3}$/);

      await section.getByRole('heading', { name: title, exact: true }).hover();
      await expect(tooltip).not.toBeVisible();
    }
  }
});
