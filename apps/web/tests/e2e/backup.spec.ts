import { expect, test } from "@playwright/test";


test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/health/ready", (route) => route.fulfill({ json: { status: "ok", checks: { database: { healthy: true, path: "D:/projects/1/Hard-task1/data/hard.db" } } } }));
  await page.route("**/api/progress/summary", (route) => route.fulfill({ json: { daily_goal: { target_minutes: 25, target_exercises: 2 }, streak_days: 0, due_review_count: 0, current_experience: 0, current_level: 1 } }));
  await page.route("**/api/backup/export", (route) => route.fulfill({ json: { archive_name: "hard-export-test.zip", content_version: "sha256-content" } }));
  await page.route("**/api/backup/import", (route) => route.fulfill({ json: { content_version: "sha256-content" } }));
});

test("backup controls explain local-drive risk and use an explicit selected archive", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/settings");
  await expect(page.getByText("同一 D 盘备份不能防止硬盘损坏")).toBeVisible();
  await page.getByRole("button", { name: "创建导出包" }).click();
  await expect(page.getByText("hard-export-test.zip")).toBeVisible();
  await page.getByLabel("选择导入归档").setInputFiles({ name: "hard-export-test.zip", mimeType: "application/zip", buffer: Buffer.from("safe archive") });
  await page.getByRole("button", { name: "安全导入" }).click();
  await expect(page.getByText("导入完成，内容版本：sha256-content")).toBeVisible();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();
});
