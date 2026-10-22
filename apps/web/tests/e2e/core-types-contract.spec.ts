import { expect, test, type Page } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';

async function enterCode(page: Page, source: string) {
  const fallback = page.locator('[data-code-editor] #python-editor:visible');
  if (await fallback.count()) return fallback.fill(source);
  await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.evaluate(text => navigator.clipboard.writeText(text), source);
  await page.locator('[data-code-editor] .monaco-editor:visible').last().click();
  await page.keyboard.press('Control+A');
  await page.keyboard.press('Control+V');
}

for (const [client, width] of [['desktop', 1440], ['mobile', 390]] as const) {
  test(`conversion contract accepts a normal answer and rejects decimal truncation (${client})`, async ({ page }) => {
    await page.setExtraHTTPHeaders({ 'X-Hard-E2E-Client': client });
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/lesson/python-core-types-conversion');
    await expect(page.locator('.lesson-content__body')).toContainText('ValueError');
    await page.getByRole('link', { name: '完成阅读，进入本课练习' }).click();
    await page.getByRole('button', { name: /^代码题(?:\s|$)/ }).click();
    await expect(page.locator(".code-exercise > p").filter({ hasText: /不能转换的文本（如 3.5、abc）/ })).toBeVisible();
    const source = 'import sys\ntry:\n    number = int(sys.stdin.read().strip())\nexcept ValueError:\n    sys.exit(1)\nprint(number + 1)\n';
    await enterCode(page, source.replace('int(sys.stdin.read().strip())', 'int(float(sys.stdin.read().strip()))'));
    await page.getByRole('button', { name: '运行代码', exact: true }).click();
    if (client === 'mobile') await page.getByRole('button', { name: '结果', exact: true }).click();
    await expect(page.getByRole('heading', { name: '运行状态：运行失败', exact: true })).toBeVisible({ timeout: 15000 });
    if (client === 'mobile') await page.getByRole('button', { name: '编辑器', exact: true }).click();
    await enterCode(page, source);
    await page.getByRole('button', { name: '运行代码', exact: true }).click();
    if (client === 'mobile') await page.getByRole('button', { name: '结果', exact: true }).click();
    await expect(page.getByRole('heading', { name: '运行状态：运行完成', exact: true })).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('公开测试：2 / 2 通过', { exact: true })).toBeVisible();
    expect(await page.content()).not.toContain('reference_solution');
    expect(await page.content()).not.toContain('__hard_hidden_');
    expect(await page.locator('html').evaluate(el => el.scrollWidth <= innerWidth)).toBe(true);
    if (process.env.HARD_VISUAL_AUDIT_DIR) {
      mkdirSync(process.env.HARD_VISUAL_AUDIT_DIR, { recursive: true });
      await page.screenshot({ path: join(process.env.HARD_VISUAL_AUDIT_DIR, `${client}-conversion.png`), fullPage: true });
    }
  });
}
