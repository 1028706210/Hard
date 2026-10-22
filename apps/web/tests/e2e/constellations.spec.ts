import { expect, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { resolve } from "node:path";

for (const width of [1440, 390]) {
  test(`real knowledge chains and cross-language mapping at ${width}px`, async ({ page, request }) => {
    await page.setExtraHTTPHeaders({ 'X-Hard-E2E-Client': width === 1440 ? 'desktop' : 'mobile' });
    await page.setViewportSize({ width, height: 900 });
    const comparison = await (await request.get('/api/compare/concepts')).json();
    const variables = comparison.concepts.find((c: {id: string}) => c.id === 'variables');
    await page.goto('/constellations');
    await expect(page.getByRole('heading', { name: '知识星图主页' })).toBeVisible();
    await expect(page.locator('[data-connection]')).toHaveCount(4);
    await expect(page).toHaveURL(/\/$/);
    await page.getByRole('button', { name: '查看模块星链' }).click();
    await page.getByLabel('切换共同概念').selectOption('variables');
    const selectedLesson = page.locator('.selected-lesson').getByRole('link', { name: '阅读课时', exact: true });
    await expect(selectedLesson).toHaveAttribute('href', `/lesson/${variables.slots.python.lesson_id}`);
    await page.getByRole('navigation', { name: '星链语言' }).getByRole('button', { name: 'Java', exact: true }).click();
    await expect(selectedLesson).toHaveAttribute('href', `/lesson/${variables.slots.java.lesson_id}`);
    await page.getByLabel('查找星链概念').fill('指针');
    await page.getByLabel('切换共同概念').selectOption({label: '指针'});
    const pointer = comparison.concepts.find((c: {name: string}) => c.name === '指针');
    for (const language of ['python', 'java', 'csharp', 'cpp']) {
      const detail = page.locator(`[data-connection-detail="${language}"]`);
      const slot = pointer.slots[language];
      if (slot.status === 'available') {
        await expect(detail).toContainText(slot.difference);
        await expect(detail.locator('a')).toHaveAttribute('href', `/lesson/${slot.lesson_id}`);
      } else {
        await expect(detail).toContainText('暂无对应课时');
        await expect(page.locator(`[data-connection="${language}"]`)).toHaveCount(0);
      }
    }
    expect(await page.locator('.constellation-page').evaluate(el => el.scrollWidth <= el.clientWidth)).toBeTruthy();
    await page.getByLabel('查找星链概念').fill('变量');
    await page.getByLabel('切换共同概念').selectOption({label: '变量'});
    const directory = resolve(process.env.HARD_UI_SCREENSHOTS ?? '../../.tool-cache/ui-screenshots');
    mkdirSync(directory, { recursive: true });
    await page.screenshot({ path: resolve(directory, `star-chain-${width}.png`), fullPage: true });
    await selectedLesson.click();
    await expect(page.locator('.lesson-content h1')).toContainText(variables.slots.java.lesson_title);
    await expect(page.locator('.lesson-content h1')).toHaveCount(1);
  });
}
