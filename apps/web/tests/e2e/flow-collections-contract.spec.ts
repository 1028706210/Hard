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
  test(`flow and collection exercises follow their public contracts (${client})`, async ({ page }) => {
    await page.setExtraHTTPHeaders({ 'X-Hard-E2E-Client': client });
    await page.setViewportSize({ width, height: 900 });
    const cases = [
      { lesson: 'python-flow-collections-conditions', label: '代码题', source: 'import sys\ntry:\n    score = int(sys.stdin.read())\nexcept ValueError:\n    sys.exit(1)\nif score < 0 or score > 100:\n    sys.exit(1)\nprint("retry" if score < 70 else "pass")\n', prompt: '大于或等于 70' },
      { lesson: 'python-flow-collections-data-structures', label: '代码题', source: 'import sys, json\ntry:\n    data = json.load(sys.stdin)\nexcept ValueError:\n    sys.exit(1)\nif type(data) is not dict:\n    sys.exit(1)\nfor group in data.values():\n    if type(group) is not list or any(type(value) is not str for value in group):\n        sys.exit(1)\nrows = data.get("beginner", [])\nprint(len(rows))\nfor value in rows:\n    print(value)\n', prompt: '保留重复项和字符串内部空格' },
      { lesson: 'python-flow-collections-while-loop', label: '挑战', source: 'import sys\ntry:\n    limit = int(sys.stdin.read())\nexcept ValueError:\n    sys.exit(1)\nif limit < 0 or limit > 100:\n    sys.exit(1)\nx = 0\nwhile x < limit:\n    x += 1\n    print(x)\n', prompt: '包含 n' },
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
        await page.screenshot({ path: join(process.env.HARD_VISUAL_AUDIT_DIR, `${client}-${item.lesson}.png`), fullPage: true });
      }
    }
  });
}
