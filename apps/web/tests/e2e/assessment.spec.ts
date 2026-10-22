import { expect, test, type Page } from "@playwright/test";

const lessonId = "python-foundations-hello-world";
const helloSource = `import sys
name = sys.stdin.read().strip()
if name == "__invalid__" or (name and not name.isalpha()):
    raise ValueError("name must contain letters only")
print(f"Hello, {name or 'World'}!")`;

async function fillPythonCode(page: Page) {
  const fallback = page.locator("[data-code-editor] #python-editor:visible");
  if (await fallback.count()) {
    await fallback.fill(helloSource);
    return;
  }
  const editor = page.locator("[data-code-editor] .monaco-editor:visible").last();
  await editor.click();
  await page.keyboard.press("Control+A");
  await page.keyboard.type(helloSource);
}

test("uses the real API for assessment scoring without exposing private runner data", async ({ page }) => {
  await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status()).toBe(200);
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.goto(`/assessment/${lessonId}`);

  await page.getByRole("radio", { name: "print", exact: true }).check();
  await page.getByRole("button", { name: "提交答案", exact: true }).click();
  await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
  await fillPythonCode(page);
  await page.getByRole("button", { name: "运行代码", exact: true }).click();
  await expect(page.getByRole("heading", { name: "运行状态：运行完成" })).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText("公开测试：1 / 1 通过", { exact: true })).toBeVisible();
  expect(await page.content()).not.toContain("hidden_");
  expect(await page.content()).not.toContain("reference_solution");
  expect(await page.content()).not.toContain("stdout");
  expect(await page.content()).not.toContain("stderr");
});

test("uses explicit mobile editor and result panels with the real assessment", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/assessment/${lessonId}`);

  await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
  await page.getByRole("button", { name: "结果", exact: true }).click();
  await expect(page.getByText("等待运行结果", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "编辑器", exact: true }).click();
  await expect(page.locator("[data-code-editor] #python-editor, [data-code-editor] .monaco-editor").first()).toBeVisible();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();
});
