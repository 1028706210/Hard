import { mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import { expect, test } from "@playwright/test";


const auditDirectory = process.env.HARD_AUDIT_SCREENSHOT_DIR ? resolve(process.env.HARD_AUDIT_SCREENSHOT_DIR, "task-18") : resolve(dirname(fileURLToPath(import.meta.url)), "../../../../.tool-cache/playwright-audit/task-18");
const lesson = {
  id: "python-foundations-hello-world",
  language: "python",
  exercises: [
    { id: "python-foundations-hello-world-k01", type: "knowledge", prompt: "哪个函数输出文本？", choices: [{ id: "a", text: "print" }], starter_code: null, visible_tests: [], experience_points: 10 },
    { id: "python-foundations-hello-world-c01", type: "code", prompt: "输出 Hello", choices: [], starter_code: "print('')", visible_tests: ["输出 Hello"], experience_points: 20 },
  ],
};

function codeEditor(page: import("@playwright/test").Page) {
  return page.locator(".monaco-editor").or(page.locator("#python-editor"));
}

async function replaceCode(page: import("@playwright/test").Page, source: string) {
  await codeEditor(page).click();
  await page.keyboard.press("Control+A");
  await page.keyboard.type(source);
}


test.beforeEach(async ({ page }) => {
  await page.route(`**/api/content/lessons/${lesson.id}`, (route) => route.fulfill({ json: lesson }));
  await page.route("**/api/runners/submissions", (route) => route.fulfill({ json: { id: "job-1", status: "succeeded", result: { status: "succeeded", stdout: "Hello", diagnostics: [], duration_ms: 8, tests: { visible_passed: 1, visible_total: 1, hidden_passed: 0, hidden_total: 1 } } } }));
  await page.route("**/api/assessment/attempts", (route) => route.fulfill({ json: { question_score: 100, total_score: 70, passed: true, mastery: "passed", newly_unlocked: [], experience_candidate: true, review_status: "none" } }));
});


test("scores knowledge and trusted code runs without exposing private runner data", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.goto(`/assessment/${lesson.id}`);

  await page.getByRole("button", { name: "print" }).click();
  await page.getByRole("button", { name: "提交答案" }).click();
  await expect(page.getByText("本题得分：100")).toBeVisible();
  await page.getByRole("button", { name: "代码题" }).click();
  await expect(page.locator(".monaco-editor")).toBeVisible();
  await replaceCode(page, "print('Hello')");
  await page.getByRole("button", { name: "运行代码" }).click();
  await expect(page.getByText("隐藏测试失败：1")).toBeVisible();
  expect(await page.content()).not.toContain("reference_solution");
  expect(await page.content()).not.toContain("hidden_tests");

  mkdirSync(auditDirectory, { recursive: true });
  await page.screenshot({ path: resolve(auditDirectory, "desktop-1440x1024.png"), fullPage: true });
});


test("mobile uses explicit editor and result panels", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/assessment/${lesson.id}`);

  await page.getByRole("button", { name: "代码题" }).click();
  await page.getByRole("button", { name: "结果" }).click();
  await expect(page.getByText("等待运行结果")).toBeVisible();
  await page.getByRole("button", { name: "编辑器" }).click();
  await expect(codeEditor(page)).toBeVisible();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();

  mkdirSync(auditDirectory, { recursive: true });
  await page.screenshot({ path: resolve(auditDirectory, "mobile-390x844.png"), fullPage: true });
});
