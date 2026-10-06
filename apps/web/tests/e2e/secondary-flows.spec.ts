import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";


const auditDirectory = process.env.HARD_AUDIT_SCREENSHOT_DIR ? resolve(process.env.HARD_AUDIT_SCREENSHOT_DIR, "task-19") : resolve(dirname(fileURLToPath(import.meta.url)), "../../../../.tool-cache/playwright-audit/task-19");
const lessonId = "python-foundations-hello-world";

test.beforeEach(async ({ page }) => {
  await page.route("**/api/review/queue", (route) => route.fulfill({ json: { items: [{ id: 7, concept_id: "python-output", lesson_id: lessonId, exercise_id: `${lessonId}-k01`, due_on: "2026-08-25", interval_days: 1, last_score: 40 }] } }));
  await page.route("**/api/review/items/7", (route) => route.fulfill({ json: { id: 7, score: 80, interval_days: 3, due_on: "2026-08-28", experience_candidate: false } }));
  await page.route("**/api/growth/weaknesses", (route) => route.fulfill({ json: { items: [{ concept_id: "python-output", score: 4, lesson_id: lessonId, exercise_id: `${lessonId}-c01` }] } }));
  await page.route("**/api/search?*", (route) => route.fulfill({ json: { results: [{ source_type: "note", language: "python", lesson_id: lessonId, title: "Hello World", snippet: "print 输出文本", anchor: "output" }] } }));
  await page.route("**/api/growth/summary", (route) => route.fulfill({ json: { total_experience: 120, level: 2, current_level_progress: 20, next_level_remaining: 80, streak_days: 3, badges: ["first_lesson"], mastery: [{ scope: "lesson", id: lessonId, score: 80 }], new_badges: [], route_completion: [] } }));
  await page.route("**/api/growth/history", (route) => route.fulfill({ json: { items: [{ id: "s1", exercise_id: `${lessonId}-c01`, language: "python", source_code: "print('safe')", normalized_result: { score: 80 }, score: 80, duration_ms: 5, created_at: "2026-08-25", diff: "+print('safe')" }] } }));
  await page.route("**/api/content/catalog", (route) => route.fulfill({ json: { courses: [{ language: "python", modules: [{ lessons: [{ id: lessonId }] }] }] } }));
  await page.route(`**/api/content/lessons/${lessonId}`, (route) => route.fulfill({ json: { id: lessonId, language: "python", title: "Hello World", concepts: ["python-output"] } }));
  await page.route("**/api/v1/health/ready", (route) => route.fulfill({ json: { status: "ok", checks: { database: { healthy: true, path: "D:/projects/1/Hard-task1/data/hard.db" }, python: { healthy: true, path: "D:/DevTools/python/python.exe" } } } }));
  await page.route("**/api/progress/summary", (route) => route.fulfill({ json: { daily_goal: { target_minutes: 25, target_exercises: 2 }, streak_days: 0, due_review_count: 0, current_experience: 0, current_level: 1 } }));
  await page.route("**/api/progress/daily-goal", (route) => route.fulfill({ json: { date: "2026-08-25", configured: true, target_minutes: 30, target_exercises: 3 } }));
});

test("desktop completes review, search, growth, comparison, and settings secondary flows", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.goto("/review");
  await expect(page.getByRole("heading", { name: "计划复习" })).toBeVisible();
  await expect(page.getByText("普通错题浏览")).toBeVisible();
  await page.getByRole("button", { name: "掌握（80）" }).click();
  await expect(page.getByText("下次复习：2026-08-28")).toBeVisible();

  await page.goto("/search");
  await page.getByLabel("搜索课程内容").fill("print");
  await page.getByRole("button", { name: "搜索" }).click();
  await expect(page.getByRole("link", { name: /Hello World/ })).toHaveAttribute("href", `/lesson/${lessonId}#output`);

  await page.goto("/growth");
  await expect(page.getByText("120 XP")).toBeVisible();
  await expect(page.getByText("热力图数据尚不可用")).toBeVisible();

  await page.goto("/compare");
  await expect(page.getByText("python-output")).toBeVisible();
  await expect(page.locator('[data-language="java"]')).toContainText("尚无内容");

  await page.goto("/settings");
  await expect(page.getByText("D:/DevTools/python/python.exe")).toBeVisible();
  await page.getByLabel("每日学习分钟").fill("30");
  await page.getByLabel("每日练习数量").fill("3");
  await page.getByRole("button", { name: "保存目标" }).click();
  await expect(page.getByText("目标已保存")).toBeVisible();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();

  mkdirSync(auditDirectory, { recursive: true });
  await page.screenshot({ path: resolve(auditDirectory, "desktop-1440x1024.png"), fullPage: true });
});

test("mobile exposes secondary flows without hover or horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/review");
  await page.getByRole("button", { name: "掌握（80）" }).click();
  await expect(page.getByText("下次复习：2026-08-28")).toBeVisible();
  await page.goto("/growth");
  await expect(page.getByText("代码成长历史")).toBeVisible();
  await page.goto("/settings");
  await expect(page.getByText("同一网络设备可访问数据并运行代码")).toBeVisible();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();

  mkdirSync(auditDirectory, { recursive: true });
  await page.screenshot({ path: resolve(auditDirectory, "mobile-390x844.png"), fullPage: true });
});
