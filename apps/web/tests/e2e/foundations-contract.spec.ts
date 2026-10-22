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
  test(`foundation dependency and summary exercises follow their public contracts (${client})`, async ({ page }) => {
    await page.setExtraHTTPHeaders({ 'X-Hard-E2E-Client': client });
    await page.setViewportSize({ width, height: 900 });
    const cases = [
      { lesson: 'python-foundations-virtual-environment', label: '代码题', source: 'import sys, re\nitems = [s.strip() for s in sys.stdin.read().splitlines() if s.strip()]\nif any(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", s) is None for s in items):\n    sys.exit(1)\nprint(len(set(items)))\n', prompt: '相同名称大小写敏感，只计一次' },
      { lesson: 'python-foundations-learning-resources', label: '挑战', source: 'import sys, re\nfields = [s.strip() for s in sys.stdin.read().splitlines()]\nif len(fields) != 3 or any(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", s) is None for s in fields):\n    sys.exit(1)\nfor title, value in zip(("Interpreter", "Environment", "Package"), fields):\n    print(title + ": " + value)\n', prompt: '摘要仅表示输入记录' },
    ];
    for (const item of cases) {
      await page.goto(`/lesson/${item.lesson}`);
      await page.getByRole('link', { name: '完成阅读，进入本课练习' }).click();
      await page.getByRole('button', { name: new RegExp(`^${item.label}(?:\\s|$)`) }).click();
      await expect(page.locator('.code-exercise > p').first()).toContainText(item.prompt);
      await enterCode(page, item.source);
      await page.getByRole('button', { name: '运行代码', exact: true }).click();
      if (client === 'mobile') await page.getByRole('button', { name: '结果', exact: true }).click();
      await expect(page.getByRole('heading', { name: '运行状态：运行完成', exact: true })).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('公开测试：2 / 2 通过', { exact: true })).toBeVisible();
      expect(await page.content()).not.toContain('reference_solution');
      expect(await page.content()).not.toContain('__hard_hidden_');
      expect(await page.locator('html').evaluate(el => el.scrollWidth <= innerWidth)).toBe(true);
      if (process.env.HARD_VISUAL_AUDIT_DIR) {
        mkdirSync(process.env.HARD_VISUAL_AUDIT_DIR, { recursive: true });
        await page.screenshot({ path: join(process.env.HARD_VISUAL_AUDIT_DIR, `${client}-${item.label === '挑战' ? 'summary' : 'dependencies'}.png`), fullPage: true });
      }
    }
  });
}
