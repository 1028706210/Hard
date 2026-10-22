import { expect, test, type Page } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";

type Journey = { name: "desktop" | "mobile"; width: number; height: number };
const journeys: readonly Journey[] = [
  { name: "desktop", width: 1440, height: 1024 },
  { name: "mobile", width: 390, height: 844 },
];

const csharpSource = `var value = Console.ReadLine() ?? "";
value = value.Trim();
Console.WriteLine(value.Length == 0 ? "empty" : value.ToUpperInvariant());
`;

const unsafeSource = `var tokens = (Console.ReadLine() ?? "").Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries);
if (tokens.Length < 1 || tokens.Length > 20) Environment.Exit(1);
var values = new int[tokens.Length];
for (var index = 0; index < tokens.Length; index++)
{
    if (!int.TryParse(tokens[index], out var value) || value < -1000000 || value > 1000000) Environment.Exit(1);
    values[index] = value;
}
long sum = 0;
unsafe
{
    fixed (int* start = values)
    {
        for (var index = 0; index < values.Length; index++) sum += *(start + index);
    }
}
Console.WriteLine($"sum={sum}");
`;

type RunnerJob = {
  id: string;
  status: "queued" | "running" | "succeeded" | "failed" | "timed_out";
  result?: unknown;
};

async function runCSharpSubmission(
  page: Page,
  lessonId: string,
  exerciseId: string,
  sourceCode: string,
  name: string,
  extraData: Record<string, unknown> = {},
): Promise<RunnerJob> {
  const headers = {
    "Idempotency-Key": `phase-f-e2e-${name}-${Date.now()}`,
    "X-Hard-E2E-Client": "default",
  };
  const submitted = await page.request.post("/api/runners/submissions", {
    headers,
    data: { lesson_id: lessonId, exercise_id: exerciseId, source_code: sourceCode, ...extraData },
  });
  expect(submitted.status()).toBe(200);
  const initial = (await submitted.json()) as RunnerJob;
  await expect.poll(async () => {
    const response = await page.request.get(`/api/runners/jobs/${initial.id}`, { headers });
    expect(response.status()).toBe(200);
    const job = (await response.json()) as RunnerJob;
    return ["succeeded", "failed", "timed_out"].includes(job.status);
  }, { timeout: 45_000 }).toBe(true);
  const complete = await page.request.get(`/api/runners/jobs/${initial.id}`, { headers });
  expect(complete.status()).toBe(200);
  return (await complete.json()) as RunnerJob;
}

async function fillCSharpCode(page: Page) {
  const fallback = page.locator("[data-code-editor] #csharp-editor:visible");
  if (await fallback.count()) {
    await fallback.fill(csharpSource);
    return;
  }
  const editor = page.locator("[data-code-editor] .monaco-editor:visible").last();
  await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.evaluate(async (source) => navigator.clipboard.writeText(source), csharpSource);
  await editor.click();
  await page.keyboard.press("Control+A");
  await page.keyboard.press("Control+V");
}

async function capture(page: Page, journey: Journey, step: string) {
  const auditDirectory = process.env.HARD_VISUAL_AUDIT_DIR;
  expect(auditDirectory).toBeTruthy();
  const path = join(auditDirectory!, `${journey.name}-csharp-${step}-${journey.width}x${journey.height}.png`);
  await page.screenshot({ path, fullPage: true });
  expect(existsSync(path)).toBe(true);
}

for (const journey of journeys) {
  test.describe(`C# final E2E ${journey.name}`, () => {
    test.use({
      viewport: { width: journey.width, height: journey.height },
      extraHTTPHeaders: { "X-Hard-E2E-Client": journey.name },
    });

    test("uses the real C# route, editor, runner, scoring, review and growth without private leakage", async ({ page }) => {
      await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);
      const lifecycle = await page.request.get("/api/_e2e/lifecycle");
      expect(lifecycle.status()).toBe(200);
      expect(await lifecycle.json()).toMatchObject({ lifespan: "started", application_count: 3 });

      await page.goto("/course/csharp");
      await expect(page.getByRole("heading", { name: "课程：csharp", exact: true })).toBeVisible();
      await expect(page.getByText("C# 入门、类型与控制流", { exact: true })).toBeVisible();
      await capture(page, journey, "course");

      await page.getByRole("link", { name: "C# 教程", exact: true }).click();
      await expect(page.getByRole("heading", { name: "C# 教程", exact: true }).first()).toBeVisible();
      await page.locator("#lesson-note").fill(`Phase F ${journey.name} C# note`);
      await page.getByRole("button", { name: "保存笔记", exact: true }).click();
      await expect(page.getByText("已同步", { exact: true })).toBeVisible();
      await capture(page, journey, "lesson");

      await page.goto("/assessment/csharp-foundations-tutorial");
      await page.getByRole("button", { name: /^知识题(?:\s|$)/ }).first().click();
      await page.getByRole("radio", { name: "按照规则把输入转换为结果", exact: true }).check();
      await page.getByRole("button", { name: "提交答案", exact: true }).click();
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();

      await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
      const workspace = page.locator("[data-code-editor]");
      await expect(workspace).toHaveAttribute("data-language", "csharp");
      await expect(workspace.getByText("C# 代码编辑器", { exact: true })).toBeVisible();
      await expect(workspace).not.toContainText("Java 代码编辑器");
      await expect(workspace).not.toContainText("Python 代码编辑器");
      await expect(workspace.locator(".monaco-editor:visible, textarea:visible")).toHaveCount(1);
      await fillCSharpCode(page);
      const submitted = page.waitForResponse((response) =>
        response.url().includes("/api/runners/submissions") && response.request().method() === "POST",
      );
      await page.getByRole("button", { name: "运行代码", exact: true }).click();
      const submissionResponse = await submitted;
      const payload = submissionResponse.request().postDataJSON() as { source_code: string };
      expect(payload.source_code.replaceAll("\r\n", "\n")).toBe(csharpSource);
      const submission = submissionResponse.json() as Promise<RunnerJob>;
      const jobId = (await submission).id;
      await expect.poll(async () => {
        const response = await page.request.get(`/api/runners/jobs/${jobId}`, {
          headers: { "X-Hard-E2E-Client": journey.name },
        });
        expect(response.status()).toBe(200);
        return ((await response.json()) as RunnerJob).status;
      }, { timeout: 45_000 }).toBe("succeeded");
      if (journey.name === "mobile") await page.getByRole("button", { name: "结果", exact: true }).click();
      await expect(page.getByRole("heading", { name: /运行状态：/ })).toBeVisible({ timeout: 5_000 });
      await capture(page, journey, "assessment-terminal");
      await expect(page.getByRole("heading", { name: "运行状态：运行完成", exact: true })).toBeVisible({ timeout: 20_000 });
      await expect(page.getByText("公开测试：1 / 1 通过", { exact: true })).toBeVisible();
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();
      expect(await page.content()).not.toContain("reference_solution");
      expect(await page.content()).not.toContain("hidden_");
      await capture(page, journey, "assessment");

      await page.goto("/assessment/python-foundations-hello-world");
      await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
      const pythonWorkspace = page.locator("[data-code-editor]");
      await expect(pythonWorkspace).toHaveAttribute("data-language", "python");
      await expect(pythonWorkspace.getByText("Python 代码编辑器", { exact: true })).toBeVisible();
      await expect(pythonWorkspace).not.toContainText("C# 代码编辑器");

      await page.goto("/assessment/java-foundations-tutorial");
      await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
      const javaWorkspace = page.locator("[data-code-editor]");
      await expect(javaWorkspace).toHaveAttribute("data-language", "java");
      await expect(javaWorkspace.getByText("Java 代码编辑器", { exact: true })).toBeVisible();
      await expect(javaWorkspace).not.toContainText("C# 代码编辑器");

      await page.goto("/lesson/csharp-capstone-language-quiz");
      await expect(page.getByRole("heading", { name: "C# 语言测验与结业实践", exact: true }).first()).toBeVisible();

      await page.goto("/review");
      await expect(page.getByRole("heading", { name: "复习中心", exact: true })).toBeVisible();
      await expect(page.locator("[data-review-queue]")).toBeVisible();

      await page.goto("/growth");
      await expect(page.getByRole("heading", { name: "成长报告", exact: true })).toBeVisible();
      await expect(page.locator('[data-mastery-record][data-scope-id^="csharp"]').first()).toBeVisible();
      const weaknesses = await page.request.get("/api/growth/weaknesses");
      expect(weaknesses.status()).toBe(200);
      // 全量电池下其他语言旅程可能留下弱点项；此处认证 C# 满分结业不产生 C# 弱点。
      const weaknessItems = (await weaknesses.json()).items as Array<{ lesson_id: string }>;
      expect(weaknessItems.filter((item) => item.lesson_id.startsWith("csharp"))).toEqual([]);
      await capture(page, journey, "growth");
      if (journey.name === "mobile") {
        expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();
      }
    });
  });
}

test("real C# API keeps unsafe authorization server-only and public runner results private", async ({ page }) => {
  await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);

  const clientCannotEnableUnsafe = await runCSharpSubmission(
    page,
    "csharp-foundations-tutorial",
    "csharp-foundations-tutorial-c01",
    "unsafe { int value = 7; int* pointer = &value; Console.WriteLine(*pointer); }",
    "client-unsafe-blocked",
    { allow_unsafe: true, compiler_arguments: ["/unsafe"] },
  );
  expect(clientCannotEnableUnsafe.status).toBe("failed");
  const blockedPayload = JSON.stringify(clientCannotEnableUnsafe);
  expect(blockedPayload).not.toContain("reference_solution");
  expect(blockedPayload).not.toContain("hidden_");
  expect(blockedPayload.toLowerCase()).not.toContain("/unsafe");

  const serverAllowlistedUnsafe = await runCSharpSubmission(
    page,
    "csharp-capstone-unsafe-code",
    "csharp-capstone-unsafe-code-c01",
    unsafeSource,
    "server-unsafe-allowlist",
  );
  expect(serverAllowlistedUnsafe.status).toBe("succeeded");
  const allowedPayload = JSON.stringify(serverAllowlistedUnsafe);
  expect(allowedPayload).not.toContain("reference_solution");
  expect(allowedPayload).not.toContain("hidden_");
  expect(allowedPayload).not.toContain("runner-work");
  expect(allowedPayload).not.toContain("D:\\projects");
});
