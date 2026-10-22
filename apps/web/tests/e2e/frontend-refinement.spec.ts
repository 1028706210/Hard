import { mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { expect, test } from "@playwright/test";

test.use({ extraHTTPHeaders: { "X-Hard-E2E-Client": "default" } });

test("paused stars remain readable when a module opens and can resume", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.goto("/");
  await expect(page.locator(".motion-toggle")).toBeVisible();
  await page.locator(".motion-toggle").click();
  await page.getByRole("button", { name: "Python · 变量", exact: true }).click();
  await expect(page.locator(".shared-star")).toContainText("变量");
  await expect(page.locator(".shared-star")).toHaveCSS("filter", "none");
  await expect(page.locator(".shared-star")).toHaveCSS("opacity", "1");
  await page.locator(".module-disclosure").click();
  const stars = page.locator(".star-canvas .star-node");
  await expect(stars.first()).toBeVisible();
  await expect.poll(() => stars.evaluateAll(nodes => nodes.every(node => Number(getComputedStyle(node).opacity) > 0.9))).toBe(true);
  await stars.last().click();
  await expect(stars.last()).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".selected-lesson").getByRole("link", { name: "阅读课时", exact: true })).toHaveAttribute("href", /^\/lesson\//);
  await expect(page.locator(".selected-lesson").getByRole("link", { name: "进入练习", exact: true })).toHaveAttribute("href", /^\/assessment\//);
  await page.locator(".chain-motion-toggle").click();
  await expect(page.locator(".motion-toggle")).toHaveAttribute("aria-pressed", "false");
  const flow = page.locator(".star-canvas .chain-flow");
  const before = await flow.evaluate(node => getComputedStyle(node).strokeDashoffset);
  await expect.poll(() => flow.evaluate(node => getComputedStyle(node).strokeDashoffset)).not.toBe(before);
});

test("every real concept remains reachable across comparison pages", async ({ page }) => {
  await page.goto("/compare");
  const response = await page.request.get("/api/compare/concepts");
  const payload = await response.json();
  const seen: string[] = [];
  const next = page.locator("[data-next-concepts]").first();
  await expect(page.locator("[data-concept-card]").first()).toBeVisible();
  for (;;) {
    seen.push(...await page.locator("[data-concept-card]").evaluateAll(nodes => nodes.map(node => node.getAttribute("data-concept-card")!)));
    if (await next.isDisabled()) break;
    const previous = await page.locator("[data-concept-card]").first().getAttribute("data-concept-card");
    await next.click();
    await expect(page.locator("[data-concept-card]").first()).not.toHaveAttribute("data-concept-card", previous!);
  }
  expect(seen.sort()).toEqual(payload.concepts.map((concept: { id: string }) => concept.id).sort());
  expect(new Set(seen).size).toBe(seen.length);
  await page.locator("[data-concept-filter]").fill("variables");
  await expect(page.locator("[data-concept-card]")).toHaveCount(1);
  await expect(page.locator("[data-concept-card='variables'] [data-language]")).toHaveCount(4);
});

for (const width of [390, 768]) {
  test(`all main pages remain readable at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    const routes = [
      ["home", "/"], ["course", "/course/python"],
      ["lesson", "/lesson/python-modules-io-oop-classes"],
      ["assessment", "/assessment/python-modules-io-oop-classes"],
      ["review", "/review"], ["search", "/search"], ["compare", "/compare"],
      ["growth", "/growth"], ["settings", "/settings"],
    ];
    const directory = resolve(process.env.HARD_VISUAL_AUDIT_DIR ?? "../../.tool-cache/frontend-refinement", `responsive-${width}`);
    mkdirSync(directory, { recursive: true });
    for (const [label, route] of routes) {
      await page.goto(route);
      await expect(page.getByRole("heading", { level: 1 }).first()).toBeVisible();
      await expect(page.getByRole("alert").filter({ hasText: /\S/ })).toHaveCount(0);
      await expect.poll(() => page.locator("html").evaluate(node => node.scrollWidth <= window.innerWidth)).toBe(true);
      await page.screenshot({ path: resolve(directory, `${label}.png`), fullPage: true });
    }
  });
}
