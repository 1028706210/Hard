import { expect, test, type Page } from "@playwright/test";
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

type Journey = { name: "desktop" | "mobile"; width: number; height: number };
const journeys: readonly Journey[] = [
  { name: "desktop", width: 1440, height: 1024 },
  { name: "mobile", width: 390, height: 844 },
];

const helloSource = `import sys
name = sys.stdin.read().strip()
if name == "__invalid__" or (name and not name.isalpha()):
    raise ValueError("name must contain letters only")
print(f"Hello, {name or 'World'}!")`;
async function fillPythonCode(page: Page, source: string) {
  const fallback = page.locator("[data-code-editor] #python-editor:visible");
  if (await fallback.count()) {
    await fallback.fill(source);
    return;
  }
  const editor = page.locator("[data-code-editor] .monaco-editor:visible").last();
  await editor.click();
  await page.keyboard.press("Control+A");
  await page.keyboard.type(source);
}

async function capture(page: Page, journey: Journey, step: string) {
  const auditDirectory = process.env.HARD_VISUAL_AUDIT_DIR;
  if (!auditDirectory) return;
  const path = join(auditDirectory, `${journey.name}-${step}-${journey.width}x${journey.height}.png`);
  await page.screenshot({ path });
  expect(existsSync(path)).toBe(true);
}

for (const journey of journeys) {
  test.describe(`Python milestone ${journey.name}`, () => {
    test.use({
      viewport: { width: journey.width, height: journey.height },
      extraHTTPHeaders: { "X-Hard-E2E-Client": journey.name },
    });

    test("uses an isolated real API, runner, scoring, review, backup and growth journey", async ({ page }) => {
      await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status()).toBe(200);
      await page.goto("/");
      await capture(page, journey, "home-start");

      if (journey.name === "mobile") {
        await page.getByRole("button", { name: "打开导航" }).click();
        await page.getByRole("link", { name: "当前课时", exact: true }).click();
      } else {
        await page.locator("[data-continue-learning]").click();
      }
      await expect(page.getByRole("heading", { name: "Hello World", exact: true }).first()).toBeVisible();
      if (journey.name === "mobile") {
        await page.getByRole("button", { name: "打开课时目录" }).click();
        await expect(page.getByRole("navigation", { name: "课时目录" })).toBeVisible();
        await page.getByRole("button", { name: "关闭课时目录" }).click();
      }
      await page.locator("#lesson-note").fill(`Phase D ${journey.name} 真实笔记`);
      await page.getByRole("button", { name: "保存笔记", exact: true }).click();
      await expect(page.getByText("已同步", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: "收藏课时", exact: true }).click();
      await expect(page.getByRole("button", { name: "取消收藏", exact: true })).toBeVisible();
      await capture(page, journey, "lesson");

      await page.goto("/search");
      await page.getByRole("searchbox", { name: "搜索课程内容" }).fill(`Phase D ${journey.name} 真实笔记`);
      await page.getByRole("button", { name: "搜索", exact: true }).click();
      await expect(page.locator(".result-snippet")).toContainText(new RegExp(`\\[Phase\\].*\\[D\\].*\\[${journey.name}\\]`));

      await page.goto("/assessment/python-foundations-hello-world");
      await page.getByRole("button", { name: "input", exact: true }).click();
      await page.getByRole("button", { name: "提交答案", exact: true }).click();
      await expect(page.getByText("本题得分：0", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: "知识题", exact: true }).nth(1).click();
      await page.getByRole("button", { name: "文件顶部", exact: true }).click();
      await page.getByRole("button", { name: "提交答案", exact: true }).click();
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: "知识题", exact: true }).nth(2).click();
      await page.getByRole("button", { name: "是", exact: true }).click();
      await page.getByRole("button", { name: "提交答案", exact: true }).click();
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();

      await page.getByText("代码题", { exact: true }).click();
      await fillPythonCode(page, helloSource);
      await page.getByRole("button", { name: "运行代码", exact: true }).click();
      if (journey.name === "mobile") await page.getByRole("button", { name: "结果", exact: true }).click();
      await expect(page.getByRole("heading", { name: "运行状态：succeeded" })).toBeVisible({ timeout: 15_000 });
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();
      await capture(page, journey, "assessment");

      await page.goto("/review");
      await expect(page.locator("[data-review-queue]").getByText("variables", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: "掌握（80）", exact: true }).click();
      await expect(page.getByText(/下次复习：/)).toBeVisible();

      await page.goto("/");
      await expect(page.locator('[data-map-world="python"]')).toContainText("学习中");
      if (journey.name === "mobile") await expect(page.locator('[data-route-node="python"]')).toContainText("学习中");

      const beforeExport = await (await page.request.get("/api/progress/summary")).json();
      await page.goto("/settings");
      await page.getByRole("button", { name: "创建导出包", exact: true }).click();
      const archive = page.locator("[data-export-name]");
      await expect(archive).toContainText("hard-export-");
      const archiveName = (await archive.textContent())?.replace("已保存至 exports/", "").trim();
      expect(archiveName).toMatch(/^hard-export-[a-f0-9]{24}\.zip$/);
      const runId = process.env.HARD_E2E_RUN_ID;
      expect(runId).toMatch(/^run-\d+$/);
      const archiveBytes = await readFile(join(process.cwd(), "..", "..", ".tool-cache", `live-e2e-${runId}`, journey.name, "exports", archiveName!));
      const changed = await page.request.patch("/api/progress/lessons/python-foundations-hello-world", {
        headers: { "Idempotency-Key": `phase-d-${journey.name}-after-export-position` },
        data: { position: 999, time_spent_seconds: 0 },
      });
      expect(changed.status()).toBe(200);
      await page.locator('input[type="file"]').setInputFiles({ name: archiveName!, mimeType: "application/zip", buffer: archiveBytes });
      await page.getByRole("button", { name: "安全导入", exact: true }).click();
      await expect(page.getByText(/导入完成，内容版本：/)).toBeVisible();
      const afterImport = await (await page.request.get("/api/progress/summary")).json();
      expect(afterImport.continue_learning.position).toBe(beforeExport.continue_learning.position);

      await page.goto("/growth");
      await expect(page.getByRole("heading", { name: "成长报告", exact: true })).toBeVisible();
      await expect(page.locator("[data-mastery-record]").first()).toContainText(/模块|课程/);
      await capture(page, journey, "growth");
    });
  });
}
