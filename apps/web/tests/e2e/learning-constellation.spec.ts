import { expect, test } from '@playwright/test';
import { join } from 'node:path';

for (const [client, width] of [['desktop', 1440], ['mobile', 390]] as const) {
  test(`constellation reflects saved learning after a real lesson visit and reload (${client})`, async ({ page }) => {
    await page.setViewportSize({ width, height: 950 });
    await page.setExtraHTTPHeaders({ 'X-Hard-E2E-Client': client });
    await page.goto('/');
    const node = page.getByRole('button', { name: 'Python · 函数', exact: true });
    await expect(node).toBeVisible();
    await page.locator('[data-connection-detail="python"] a').click();
    await expect(page).toHaveURL(/\/lesson\/python-functions-iteration-functions$/);
    await expect.poll(async () => {
      const response = await page.request.get('/api/progress/summary', { headers: { 'X-Hard-E2E-Client': client } });
      return (await response.json()).lesson_statuses['python-functions-iteration-functions'];
    }).toBe('in_progress');
    await page.goto('/');
    await expect(node.locator('[data-learning-state]')).toHaveAttribute('data-learning-state', 'in_progress');
    await page.reload();
    await expect(node).toContainText('学习中');
    await page.getByRole('button', { name: 'Java · 函数', exact: true }).click();
    await page.getByRole('button', { name: '查看模块星链', exact: true }).click();
    await expect(page.getByRole('navigation', { name: '星链语言' }).getByRole('button', { name: 'Java', exact: true })).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('.selected-lesson').getByRole('link', { name: '进入练习' })).toHaveAttribute('href', '/assessment/java-core-api-methods');
    expect(await page.locator('html').evaluate(el => el.scrollWidth <= window.innerWidth)).toBeTruthy();
    if (process.env.HARD_VISUAL_AUDIT_DIR) {
      await page.screenshot({ path: join(process.env.HARD_VISUAL_AUDIT_DIR, `${client}-learning-constellation.png`), fullPage: true });
    }
  });
}
