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
  test(`remaining Python and Java exercises follow their public contracts (${client})`, async ({ page }) => {
    test.setTimeout(120000);
    await page.setExtraHTTPHeaders({ 'X-Hard-E2E-Client': client });
    await page.setViewportSize({ width, height: 900 });
    const cases = [
  {
    "lesson": "python-stdlib-data-date-time",
    "label": "代码题",
    "source": "import sys, re\nfrom datetime import date\ns = sys.stdin.read().strip()\nif not re.fullmatch(r\"[0-9]{4}-[0-9]{2}-[0-9]{2}\", s):\n    sys.exit(1)\ntry:\n    print(date.fromisoformat(s).isoformat())\nexcept ValueError:\n    sys.exit(1)\n",
    "prompt": "YYYY-MM-DD"
  },
  {
    "lesson": "python-stdlib-data-re",
    "label": "代码题",
    "source": "import sys,re\nprint(re.fullmatch(\"[a-z]+\",sys.stdin.read().rstrip(\"\\n\")) is not None)\n",
    "prompt": "[a-z]+"
  },
  {
    "lesson": "python-concurrency-network-asyncio",
    "label": "代码题",
    "source": "import asyncio,sys\ntext=sys.stdin.read().strip()\nif not text:\n    sys.exit(1)\nasync def work():\n    await asyncio.sleep(0)\n    return text.upper()\nasync def main():\n    task=asyncio.create_task(work())\n    if text==\"cancel\":\n        task.cancel()\n    try:\n        print(await task)\n    except asyncio.CancelledError:\n        print(\"cancelled\")\nasyncio.run(main())\n",
    "prompt": "cancel"
  },
  {
    "lesson": "python-automation-ui-web-markdown",
    "label": "代码题",
    "source": "import sys\ns=sys.stdin.read().rstrip(\"\\n\")\nprint(s.startswith(\"# \") and bool(s[2:].strip()) and \"\\n\" not in s)\n",
    "prompt": "# "
  },
  {
    "lesson": "python-database-deployment-pymysql",
    "label": "代码题",
    "source": "import sys,json\ntry:\n    value=json.loads(sys.stdin.read())\n    if type(value) is not bool:\n        raise ValueError()\nexcept (ValueError,TypeError):\n    sys.exit(1)\nprint(\"commit\" if value else \"rollback\")\n",
    "prompt": "JSON"
  },
  {
    "lesson": "python-capstone-examples",
    "label": "代码题",
    "source": "import sys\ntry:\n    n=int(sys.stdin.read().strip())\nexcept ValueError:\n    sys.exit(1)\nif not 0<=n<=100:\n    sys.exit(1)\nprint(n>=60)\n",
    "prompt": "60"
  },
  {
    "lesson": "java-foundations-basic-data-types",
    "label": "代码题",
    "source": "import java.nio.charset.StandardCharsets;\npublic class Main { public static void main(String[] args) throws Exception {\nString input = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();\nlong value; try { value = Long.parseLong(input); } catch (NumberFormatException error) {System.exit(1);return;}\nSystem.out.println(value >= -2147483648L && value <= 2147483647L);\n}}\n",
    "prompt": "Integer.MAX_VALUE"
  },
  {
    "lesson": "java-foundations-conditions",
    "label": "代码题",
    "source": "import java.nio.charset.StandardCharsets;\npublic class Main { public static void main(String[] args) throws Exception {\nString input = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();\nlong value; try { value = Long.parseLong(input); } catch (NumberFormatException error) {System.exit(1);return;}\nif (value < 0 || value > 100) {System.exit(1);return;}\nSystem.out.println(value >= 60 ? \"pass\" : \"retry\");\n}}\n",
    "prompt": "n>=60"
  }
];
    for (const item of cases) {
      await page.goto(`/lesson/${item.lesson}`);
      await page.getByRole('link', { name: '完成阅读，进入本课练习' }).click();
      await page.getByRole('button', { name: new RegExp(`^${item.label}(?:\\s|$)`) }).click();
      await expect(page.locator('.code-exercise > p').first()).toContainText(item.prompt);
      await enterCode(page, item.source);
      await page.getByRole('button', { name: '运行代码', exact: true }).click();
      if (client === 'mobile') await page.getByRole('button', { name: '结果', exact: true }).click();
      await expect(page.getByRole('heading', { name: '运行状态：运行完成', exact: true })).toBeVisible({ timeout: 30000 });
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
