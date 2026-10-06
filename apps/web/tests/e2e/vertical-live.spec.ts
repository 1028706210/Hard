import { expect, test } from "@playwright/test";

test("real local stack follows home through lesson runner scoring and growth without API routing mocks", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);
  await page.goto("/");
  await expect(page.locator("[data-continue-learning]")).toBeVisible();
  await page.locator("[data-continue-learning]").click();
  await expect(page.getByRole("heading", { name: "Hello World", exact: true }).first()).toBeVisible();
  await page.goto("/assessment/python-foundations-hello-world");
  await page.getByText("代码题").click();
  await page.getByRole("textbox").fill(`import sys
name = sys.stdin.read().strip()
if name == "__invalid__" or (name and not name.isalpha()):
    raise ValueError("name must contain letters only")
print(f"Hello, {name or 'World'}!")`);
  await page.getByRole("button", { name: "运行" }).click();
  await expect(page.getByRole("heading", { name: "运行状态：succeeded" })).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText("本题得分：100")).toBeVisible();
  await page.goto("/");
  await expect(page.locator('[data-map-world="python"]')).toContainText("学习中");
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator('[data-route-node="python"]')).toContainText("学习中");
  await page.goto("/growth");
  await expect(page.getByRole("heading", { name: "成长报告", exact: true })).toBeVisible();
  await expect(page.locator("[data-mastery-record]").filter({ hasText: /模块 · python-foundations|课程 · python/ }).first()).toBeVisible();
});
