import { expect, test, type Page } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";

type Journey = { name: "desktop" | "mobile"; width: number; height: number };
const journeys: readonly Journey[] = [
  { name: "desktop", width: 1440, height: 1024 },
  { name: "mobile", width: 390, height: 844 },
];

const javaSource = `import java.nio.charset.StandardCharsets;

public class Main {
    public static void main(String[] args) throws Exception {
        String value = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        if (value.isEmpty()) System.exit(1);
        System.out.println("Hello, " + value);
    }
}`;

type RunnerJob = {
  id: string;
  status: "queued" | "running" | "succeeded" | "failed" | "timed_out";
  result?: unknown;
};

function javaCourseSource(fileOperation: string) {
  return `public class Main {
    public static void main(String[] args) throws Exception {
        ${fileOperation}
        String value = new String(System.in.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8).trim();
        if (value.isEmpty()) System.exit(1);
        System.out.println("Hello, " + value);
    }
}`;
}

async function runJavaSubmission(page: Page, sourceCode: string, name: string): Promise<RunnerJob> {
  const headers = {
    "Idempotency-Key": `phase-e-final-${name}-${Date.now()}`,
    "X-Hard-E2E-Client": "default",
  };
  const submitted = await page.request.post("/api/runners/submissions", {
    headers,
    data: {
      lesson_id: "java-foundations-tutorial",
      exercise_id: "java-foundations-tutorial-c01",
      source_code: sourceCode,
    },
  });
  expect(submitted.status()).toBe(200);
  const initial = (await submitted.json()) as RunnerJob;
  await expect.poll(async () => {
    const response = await page.request.get(`/api/runners/jobs/${initial.id}`, { headers });
    expect(response.status()).toBe(200);
    const job = (await response.json()) as RunnerJob;
    return job.status === "succeeded" || job.status === "failed" || job.status === "timed_out";
  }, { timeout: 25_000 }).toBe(true);
  const complete = await page.request.get(`/api/runners/jobs/${initial.id}`, { headers });
  expect(complete.status()).toBe(200);
  return (await complete.json()) as RunnerJob;
}

async function fillJavaCode(page: Page) {
  const fallback = page.locator("[data-code-editor] #java-editor:visible");
  if (await fallback.count()) {
    await fallback.fill(javaSource);
    return;
  }
  const editor = page.locator("[data-code-editor] .monaco-editor:visible").last();
  await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.evaluate(async (source) => navigator.clipboard.writeText(source), javaSource);
  await editor.click();
  await page.keyboard.press("Control+A");
  await page.keyboard.press("Control+V");
}

async function capture(page: Page, journey: Journey, step: string) {
  const auditDirectory = process.env.HARD_VISUAL_AUDIT_DIR;
  expect(auditDirectory).toBeTruthy();
  const path = join(auditDirectory!, `${journey.name}-java-${step}-${journey.width}x${journey.height}.png`);
  await page.screenshot({ path, fullPage: true });
  expect(existsSync(path)).toBe(true);
}

for (const journey of journeys) {
  test.describe(`Java final audit ${journey.name}`, () => {
    test.use({
      viewport: { width: journey.width, height: journey.height },
      extraHTTPHeaders: { "X-Hard-E2E-Client": journey.name },
    });

    test("uses the real Java route, editor, runner, scoring, review and growth without private leakage", async ({ page }) => {
      await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);

      await page.goto("/course/java");
      await expect(page.getByRole("heading", { name: "课程：java", exact: true })).toBeVisible();
      await expect(page.getByText("Java 入门与语言基础", { exact: true })).toBeVisible();
      await capture(page, journey, "course");

      await page.getByRole("link", { name: "Java 教程", exact: true }).click();
      await expect(page.getByRole("heading", { name: "Java 教程", exact: true }).first()).toBeVisible();
      await page.locator("#lesson-note").fill(`Phase E ${journey.name} Java note`);
      await page.getByRole("button", { name: "保存笔记", exact: true }).click();
      await expect(page.getByText("已同步", { exact: true })).toBeVisible();
      await capture(page, journey, "lesson");

      await page.goto("/assessment/java-foundations-tutorial");
      await page.getByRole("button", { name: /^知识题(?:\s|$)/ }).first().click();
      await page.getByRole("radio", { name: "程序入口、编译和运行的输入、规则和输出", exact: true }).check();
      await page.getByRole("button", { name: "提交答案", exact: true }).click();
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();

      await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
      const workspace = page.locator("[data-code-editor]");
      await expect(workspace).toHaveAttribute("data-language", "java");
      await expect(workspace.getByText("Java 代码编辑器", { exact: true })).toBeVisible();
      await expect(workspace).not.toContainText("Python 代码编辑器");
      await expect(workspace.locator(".monaco-editor:visible, textarea:visible")).toHaveCount(1);
      await fillJavaCode(page);
      const submitted = page.waitForResponse((response) =>
        response.url().includes("/api/runners/submissions") && response.request().method() === "POST",
      );
      await page.getByRole("button", { name: "运行代码", exact: true }).click();
      const submissionResponse = await submitted;
      const payload = submissionResponse.request().postDataJSON() as { source_code: string };
      expect(payload.source_code.replaceAll("\r\n", "\n")).toBe(javaSource);
      const submission = submissionResponse.json() as Promise<RunnerJob>;
      const jobId = (await submission).id;
      await expect.poll(async () => {
        const response = await page.request.get(`/api/runners/jobs/${jobId}`, {
          headers: { "X-Hard-E2E-Client": journey.name },
        });
        expect(response.status()).toBe(200);
        return ((await response.json()) as RunnerJob).status;
      }, { timeout: 25_000 }).toBe("succeeded");
      if (journey.name === "mobile") await page.getByRole("button", { name: "结果", exact: true }).click();
      await expect(page.getByRole("heading", { name: /运行状态：/ })).toBeVisible({ timeout: 5_000 });
      await capture(page, journey, "assessment-terminal");
      await expect(page.getByRole("heading", { name: "运行状态：运行完成", exact: true })).toBeVisible({ timeout: 20_000 });
      await expect(page.getByText("公开测试：2 / 2 通过", { exact: true })).toBeVisible();
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();
      expect(await page.content()).not.toContain("reference_solution");
      expect(await page.content()).not.toContain("hidden_");
      await capture(page, journey, "assessment");

      await page.goto("/assessment/python-foundations-hello-world");
      await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
      const pythonWorkspace = page.locator("[data-code-editor]");
      await expect(pythonWorkspace).toHaveAttribute("data-language", "python");
      await expect(pythonWorkspace.getByText("Python 代码编辑器", { exact: true })).toBeVisible();
      await expect(pythonWorkspace).not.toContainText("Java 代码编辑器");

      await page.goto("/lesson/java-capstone-quiz");
      await expect(page.getByRole("heading", { name: "Java 测验", exact: true }).first()).toBeVisible();

      await page.goto("/review");
      await expect(page.getByRole("heading", { name: "复习中心", exact: true })).toBeVisible();
      await expect(page.locator("[data-review-queue]")).toBeVisible();

      await page.goto("/growth");
      await expect(page.getByRole("heading", { name: "成长报告", exact: true })).toBeVisible();
      await expect(page.locator('[data-mastery-record][data-scope-id^="java"]').first()).toBeVisible();
      await capture(page, journey, "growth");
      if (journey.name === "mobile") {
        expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();
      }
    });
  });
}

test("real Java API blocks external and normalized file access without leaking private data", async ({ page }) => {
  await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);
  const blockedCases = [
    ["absolute", javaCourseSource('java.nio.file.Files.readString(java.nio.file.Path.of("C:\\\\Windows\\\\win.ini"), java.nio.charset.StandardCharsets.UTF_8);')],
    ["parent", javaCourseSource('java.nio.file.Files.readString(java.nio.file.Path.of("..", "..", "outside-java-sentinel.txt").normalize(), java.nio.charset.StandardCharsets.UTF_8);')],
    ["security-manager", javaCourseSource('System.setSecurityManager(null); java.nio.file.Files.readString(java.nio.file.Path.of("C:\\\\Windows\\\\win.ini"), java.nio.charset.StandardCharsets.UTF_8);')],
    ["reflection", javaCourseSource('Class<?> files = Class.forName("java.nio.file.Files"); java.lang.reflect.Method read = files.getMethod("readString", java.nio.file.Path.class, java.nio.charset.Charset.class); read.invoke(null, java.nio.file.Path.of("C:\\\\Windows\\\\win.ini"), java.nio.charset.StandardCharsets.UTF_8);')],
  ] as const;
  for (const [name, sourceCode] of blockedCases) {
    const job = await runJavaSubmission(page, sourceCode, name);
    expect(job.status).toBe("failed");
    const publicPayload = JSON.stringify(job);
    expect(publicPayload).not.toContain("C:\\Windows");
    expect(publicPayload).not.toContain("win.ini");
    expect(publicPayload).not.toContain("outside-java-sentinel");
    expect(publicPayload).not.toContain("hidden_");
    expect(publicPayload).not.toContain("reference_solution");
  }

  const allowed = await runJavaSubmission(
    page,
    javaCourseSource('java.nio.file.Path file = java.nio.file.Path.of("lesson.txt"); java.nio.file.Files.writeString(file, "课程文件", java.nio.charset.StandardCharsets.UTF_8); java.nio.file.Files.readString(file, java.nio.charset.StandardCharsets.UTF_8);'),
    "workspace-relative",
  );
  expect(allowed.status).toBe("succeeded");
});
