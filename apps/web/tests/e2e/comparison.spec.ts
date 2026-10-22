import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test, type Page } from "@playwright/test";


const auditDirectory = process.env.HARD_TASK55_AUDIT_DIR
  ? resolve(process.env.HARD_TASK55_AUDIT_DIR)
  : resolve(dirname(fileURLToPath(import.meta.url)), "../../../../docs/audit/task-55/screenshots");

async function assertNoHorizontalOverflow(page: Page) {
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();
}

test.describe("compare desktop", () => {
  test.use({ viewport: { width: 1440, height: 1024 }, extraHTTPHeaders: { "X-Hard-E2E-Client": "desktop" } });

  test("maps every concept slot with real lessons, filter and escaped code", async ({ page }) => {
    await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);
    await page.goto("/compare");
    await expect(page.getByRole("heading", { name: "跨语言对照" })).toBeVisible();

    const variables = page.locator("[data-concept-card='variables']");
    await expect(variables).toBeVisible();
    await expect(variables.locator("[data-language]")).toHaveCount(4);
    for (const language of ["python", "java", "csharp", "cpp"]) {
      await expect(variables.locator(`[data-language='${language}'] a`)).toHaveAttribute("href", /^\/lesson\//);
    }
    await expect(variables.locator("[data-language='python'] pre code")).toContainText("count = 10");
    await expect(variables.locator("[data-language='python'] .difference")).toContainText("动态类型");

    await page.locator("[data-concept-filter]").fill("pointers");
    const pointers = page.locator("[data-concept-card='pointers']");
    await expect(pointers).toBeVisible();
    await expect(page.locator("[data-concept-card]")).toHaveCount(1);
    await expect(pointers.locator("[data-language='cpp'] a")).toHaveAttribute("href", "/lesson/cpp-core-memory-pointers");
    await expect(pointers.locator("[data-language='python'] [data-missing-slot]")).toContainText("缺失");
    await expect(pointers.locator("[data-language='python'] .note")).toContainText("没有可操作的指针");

    await page.locator("[data-concept-filter]").fill("不存在的概念");
    await expect(page.locator("[data-empty-state]")).toContainText("没有匹配当前筛选的概念");

    await page.locator("[data-concept-filter]").fill("variables");
    await variables.locator("[data-language='python'] a").click();
    await expect(page.getByRole("heading", { name: "Python 基础语法" }).first()).toBeVisible();
    expect(await page.content()).not.toContain("reference_solution");

    await assertNoHorizontalOverflow(page);
    mkdirSync(auditDirectory, { recursive: true });
    await page.goto("/compare");
    await expect(page.locator("[data-concept-card='variables']")).toBeVisible();
    await page.screenshot({ path: resolve(auditDirectory, "desktop-compare-1440x1024.png"), fullPage: true });
  });
});

test.describe("compare mobile", () => {
  test.use({ viewport: { width: 390, height: 844 }, extraHTTPHeaders: { "X-Hard-E2E-Client": "mobile" } });

  test("maps concepts vertically with filter, missing slots and lesson round-trip", async ({ page }) => {
    await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);
    await page.goto("/compare");
    await expect(page.getByRole("heading", { name: "跨语言对照" })).toBeVisible();

    const variables = page.locator("[data-concept-card='variables']");
    await expect(variables).toBeVisible();
    await expect(variables.locator("[data-language]")).toHaveCount(4);

    await page.locator("[data-concept-filter]").fill("pointers");
    const pointers = page.locator("[data-concept-card='pointers']");
    await expect(pointers.locator("[data-language='cpp'] a")).toHaveAttribute("href", "/lesson/cpp-core-memory-pointers");
    await expect(pointers.locator("[data-language='csharp'] [data-missing-slot]")).toBeVisible();

    await page.locator("[data-concept-filter]").fill("pointers");
    await pointers.locator("[data-language='cpp'] a").click();
    await expect(page.getByRole("heading", { name: "C++ 指针" }).first()).toBeVisible();
    await page.goBack();
    await expect(page.locator("[data-concept-card='pointers']")).toBeVisible();

    await assertNoHorizontalOverflow(page);
    mkdirSync(auditDirectory, { recursive: true });
    await page.locator("[data-concept-filter]").fill("");
    await expect(page.locator("[data-concept-card='variables']")).toBeVisible();
    await page.screenshot({ path: resolve(auditDirectory, "mobile-compare-390x844.png"), fullPage: true });
  });
});
