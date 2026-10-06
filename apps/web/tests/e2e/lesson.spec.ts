import { mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import { expect, test } from "@playwright/test";


const auditDirectory = process.env.HARD_AUDIT_SCREENSHOT_DIR ? resolve(process.env.HARD_AUDIT_SCREENSHOT_DIR, "task-17") : resolve(dirname(fileURLToPath(import.meta.url)), "../../../../.tool-cache/playwright-audit/task-17");
const lesson = {
  id: "python-foundations-hello-world",
  title: "Hello World",
  language: "python",
  module_id: "python-foundations",
  objectives: ["输出文本"],
  concepts: ["python-output"],
  difficulty: "beginner",
  rendered_html: "<h2>Hello World</h2><p>使用 <code>print</code> 输出文本。</p>",
  source_url: "https://www.runoob.com/python3/python3-hello-world.html",
  source_snapshot_date: "2026-08-23",
  exercises: [],
};
const course = { language: "python", title: "Python", fixture_only: true, modules: [{ id: "python-foundations", title: "Python 基础", prerequisites: [], lessons: [{ id: lesson.id, title: lesson.title, locked: false }] }] };


test.beforeEach(async ({ page }) => {
  await page.route("**/api/content/courses/python", (route) => route.fulfill({ json: course }));
  await page.route(`**/api/content/lessons/${lesson.id}`, (route) => route.fulfill({ json: lesson }));
  await page.route("**/api/progress/**", (route) => route.fulfill({ json: { lesson_id: lesson.id, position: 1, time_spent_seconds: 1, status: "in_progress", updated_at: "now", favorite: true, body: "笔记" } }));
});


test("lesson workspace saves notes and favorites without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.goto(`/lesson/${lesson.id}`);

  await expect(page.getByRole("heading", { name: "Hello World", level: 1 })).toBeVisible();
  await page.getByLabel("课时笔记").fill("我的笔记");
  await page.getByRole("button", { name: "保存笔记" }).click();
  await page.getByRole("button", { name: "收藏课时" }).click();
  await expect(page.getByRole("link", { name: "来源：菜鸟教程" })).toHaveAttribute("href", lesson.source_url);
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();

  mkdirSync(auditDirectory, { recursive: true });
  await page.screenshot({ path: resolve(auditDirectory, "desktop-1440x1024.png"), fullPage: true });
});


test("mobile course navigation is explicitly opened and closed", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/lesson/${lesson.id}`);

  await page.getByRole("button", { name: "打开课时目录" }).click();
  await expect(page.getByRole("navigation", { name: "课时目录" })).toBeVisible();
  await page.getByRole("button", { name: "关闭课时目录" }).click();
  await expect(page.getByRole("navigation", { name: "课时目录" })).toBeHidden();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();

  mkdirSync(auditDirectory, { recursive: true });
  await page.screenshot({ path: resolve(auditDirectory, "mobile-390x844.png"), fullPage: true });
});
