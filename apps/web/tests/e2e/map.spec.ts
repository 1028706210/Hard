import { mkdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import { expect, test } from "@playwright/test";


const auditDirectory = process.env.HARD_AUDIT_SCREENSHOT_DIR ? resolve(process.env.HARD_AUDIT_SCREENSHOT_DIR, "task-16") : resolve(dirname(fileURLToPath(import.meta.url)), "../../../../.tool-cache/playwright-audit/task-16");

function expectPngDimensions(path: string, width: number, height: number) {
  const png = readFileSync(path);
  expect(png.readUInt32BE(16)).toBe(width);
  expect(png.readUInt32BE(20)).toBe(height);
}


test("desktop renders a centered orbital map with four accessible worlds", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.goto("/");

  await expect(page.locator(".orbital-map")).toBeVisible();
  await expect(page.locator("[data-map-world]")).toHaveCount(4);
  await expect(page.locator(".continue-node")).toContainText(/继续学习|尚无继续学习课时/);
  await expect(page.locator("[data-mobile-route]")).toBeHidden();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();
  const viewport = page.viewportSize();
  expect(viewport).not.toBeNull();
  const boxes = await page.locator("[data-map-world], .continue-node, .learning-metrics").evaluateAll((elements) => elements.map((element) => {
    const box = element.getBoundingClientRect();
    return { left: box.left, top: box.top, right: box.right, bottom: box.bottom };
  }));
  for (const box of boxes) {
    expect(box.left).toBeGreaterThanOrEqual(0);
    expect(box.top).toBeGreaterThanOrEqual(0);
    expect(box.right).toBeLessThanOrEqual(viewport!.width);
    expect(box.bottom).toBeLessThanOrEqual(viewport!.height);
  }

  mkdirSync(auditDirectory, { recursive: true });
  const screenshot = resolve(auditDirectory, "desktop-1440x1024.png");
  await page.screenshot({ path: screenshot, fullPage: false });
  expectPngDimensions(screenshot, 1440, 1024);
});


test("mobile changes to a vertical route with no hover-only controls", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.locator(".orbital-map")).toBeHidden();
  await expect(page.locator("[data-mobile-route]")).toBeVisible();
  await expect(page.locator("[data-route-node]")).toHaveCount(4);
  await expect(page.getByRole("link", { name: /Python/ })).toBeVisible();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();

  mkdirSync(auditDirectory, { recursive: true });
  const screenshot = resolve(auditDirectory, "mobile-390x844.png");
  await page.screenshot({ path: screenshot, fullPage: false });
  expectPngDimensions(screenshot, 390, 844);
});
