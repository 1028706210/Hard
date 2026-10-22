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
  test(`function exercises follow their public contracts (${client})`, async ({ page }) => {
    await page.setExtraHTTPHeaders({ 'X-Hard-E2E-Client': client });
    await page.setViewportSize({ width, height: 900 });
    const cases = [
      { lesson: 'python-functions-iteration-iterators', label: '代码题', source: 'import sys\ntry:\n    n = int(sys.stdin.read())\nexcept ValueError:\n    sys.exit(1)\nif not 0 <= n <= 100:\n    sys.exit(1)\ndef steps(limit):\n    current = 1\n    while current <= limit:\n        yield current\n        current += 1\ng = steps(n)\nprint(list(g))\nprint(list(g))\n', prompt: '同一个对象' },
      { lesson: 'python-functions-iteration-decorators', label: '代码题', source: 'import sys\nfrom functools import wraps\nname = sys.stdin.read().strip()\nif not name:\n    sys.exit(1)\ndef announce(original):\n    @wraps(original)\n    def call(*args, **kwargs):\n        result = original(*args, **kwargs)\n        return "run " + result\n    return call\n@announce\ndef task(name):\n    return name\nprint(task(name))\nprint(task.__name__)\n', prompt: '任意非空文本' },
      { lesson: 'python-functions-iteration-scope', label: '代码题', source: 'import sys\nparts = [line.strip() for line in sys.stdin.read().splitlines()]\nif len(parts) != 2 or any(not item for item in parts):\n    sys.exit(1)\nvalue, inner = parts\ndef show(local_value):\n    value = local_value\n    return value\nprint(show(inner))\nprint(value)\n', prompt: '不使用 global 修改外层' },
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
