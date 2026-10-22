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


test("desktop renders a homepage constellations with four accessible languages", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.goto("/");

  await expect(page.locator(".home-atlas")).toBeVisible();
  await expect(page.locator("[data-map-world]")).toHaveCount(4);
  await expect(page.locator("[data-knowledge-group]")).toHaveCount(12);
  await expect(page.locator(".concept-star")).toHaveCount(36);
  await expect(page.locator(".home-continue")).toContainText(/继续学习|尚无继续学习课时/);
  await expect(page.locator(".language-heading img")).toHaveCount(4);
  await page.getByRole("button", { name: "暂停星空动效" }).click();
  await expect(page.getByRole("button", { name: "开启星空动效" })).toHaveAttribute("aria-pressed", "true");
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();
  const viewport = page.viewportSize();
  expect(viewport).not.toBeNull();
  const boxes = await page.locator("[data-map-world], .home-continue, .learning-metrics").evaluateAll((elements) => elements.map((element) => {
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
  const animation = page.locator('.data-star').first();
  await expect(animation).toHaveCSS('animation-play-state', 'paused');
  await page.getByRole('button', { name: '开启星空动效' }).click();
  await expect(animation).toHaveCSS('animation-play-state', 'running');
  const dust = page.locator('.drifting-stars img');
  const startTransform = await dust.evaluate(el => getComputedStyle(el).transform);
  await expect.poll(() => dust.evaluate(el => getComputedStyle(el).transform)).not.toBe(startTransform);
  await page.getByRole('button', { name: '暂停星空动效' }).click();
  await expect(dust).toHaveCSS('animation-play-state', 'paused');
  await expect(page.locator('.route-flow').first()).toHaveCSS('animation-play-state', 'paused');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await expect(animation).toHaveCSS('animation-name', 'none');
  await expect(dust).toHaveCSS('animation-name', 'none');
  await expect(page.locator('.atlas-scene')).toHaveCSS('animation-name', 'none');
  await page.setViewportSize({ width: 1586, height: 992 });
  await page.screenshot({ path: resolve(auditDirectory, 'desktop-reference-1586x992.png'), fullPage: false });
});


test("mobile keeps four touch-accessible constellations and opens modules inline", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.locator(".home-atlas")).toBeVisible();
  await expect(page.locator("[data-route-node]")).toHaveCount(4);
  await expect(page.locator("[data-map-world=python] .language-heading")).toBeVisible();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();

  mkdirSync(auditDirectory, { recursive: true });
  const screenshot = resolve(auditDirectory, "mobile-390x844.png");
  await page.screenshot({ path: screenshot, fullPage: false });
  expectPngDimensions(screenshot, 390, 844);
  await page.locator("[data-map-world=python] .language-heading").click();
  await expect(page.locator('.chain-toolbar')).toBeFocused();
  await expect(page.getByRole("navigation", { name: "星链语言" })).toBeVisible();
  await expect(page.getByRole("link", { name: "打开课程目录" })).toHaveAttribute("href", "/course/python");
  const targets = await page.locator(".concept-star").evaluateAll(els => els.map(el => el.getBoundingClientRect().width));
  expect(targets.every(width => width >= 44)).toBeTruthy();
});
