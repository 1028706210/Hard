import { mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import { expect, test } from "@playwright/test";


const auditDirectory = process.env.HARD_AUDIT_SCREENSHOT_DIR ? resolve(process.env.HARD_AUDIT_SCREENSHOT_DIR, "task-15") : resolve(dirname(fileURLToPath(import.meta.url)), "../../../../.tool-cache/playwright-audit/task-15");


test("desktop shell has usable navigation and no horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.goto("/");

  await expect(page.getByRole("navigation", { name: "主导航" })).toBeVisible();
  await expect(page.getByRole("link", { name: "复习" })).toBeVisible();
  await page.getByRole("link", { name: "复习" }).click();
  await expect(page.getByRole("main")).toContainText("复习中心");
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();

  mkdirSync(auditDirectory, { recursive: true });
  await page.screenshot({ path: resolve(auditDirectory, "desktop-1440x1024.png"), fullPage: true });
});


test("mobile shell opens touch navigation without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  const menu = page.getByRole("button", { name: "打开导航" });
  await menu.click();
  await expect(menu).toHaveAttribute("aria-expanded", "true");
  await expect(page.locator("#mobile-navigation").getByRole("link", { name: "设置" })).toBeVisible();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();

  mkdirSync(auditDirectory, { recursive: true });
  await page.screenshot({ path: resolve(auditDirectory, "mobile-390x844.png"), fullPage: true });
});


test("navigation keeps keyboard focus, 44px targets, and reduced-motion support", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Hard 知识星图主页" })).toBeFocused();
  const courseLink = page.getByRole("link", { name: "课程", exact: true });
  const box = await courseLink.boundingBox();
  expect(box?.height).toBeGreaterThanOrEqual(44);
  expect(await courseLink.evaluate((element) => getComputedStyle(element).transitionDuration)).toBe("0s");
});
