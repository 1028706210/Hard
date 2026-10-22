import { expect, test, type Page } from "@playwright/test";
import { existsSync, writeFileSync } from "node:fs";
import { join } from "node:path";

type Journey = { name: "desktop" | "mobile"; width: number; height: number };
const journeys: readonly Journey[] = [
  { name: "desktop", width: 1440, height: 1024 },
  { name: "mobile", width: 390, height: 844 },
];

const cppSource = `#include <iostream>
#include <string>

int main() {
    std::string name;
    std::getline(std::cin, name);
    std::cout << "Hello, " << name << "!" << std::endl;
    return 0;
}
`;

type RunnerResult = {
  status: string;
  compile?: { passed: boolean } | null;
  tests?: { visible_passed: number; visible_total: number } | null;
  diagnostics: string[];
};

type RunnerJob = {
  id: string;
  status:
    | "queued"
    | "running"
    | "succeeded"
    | "failed"
    | "cancelled"
    | "timed_out"
    | "output_overflow"
    | "rejected"
    | "tool_missing";
  result?: RunnerResult | null;
};

async function runCppSubmission(
  page: Page,
  lessonId: string,
  exerciseId: string,
  sourceCode: string,
  name: string,
): Promise<RunnerJob> {
  const headers = {
    "Idempotency-Key": `task54-e2e-${name}-${Date.now()}`,
    "X-Hard-E2E-Client": "default",
  };
  const submitted = await page.request.post("/api/runners/submissions", {
    headers,
    data: { lesson_id: lessonId, exercise_id: exerciseId, source_code: sourceCode },
  });
  expect(submitted.status()).toBe(200);
  const initial = (await submitted.json()) as RunnerJob;
  await expect.poll(async () => {
    const response = await page.request.get(`/api/runners/jobs/${initial.id}`, { headers });
    expect(response.status()).toBe(200);
    const job = (await response.json()) as RunnerJob;
    return ["succeeded", "failed", "timed_out", "output_overflow"].includes(job.status);
  }, { timeout: 60_000 }).toBe(true);
  const complete = await page.request.get(`/api/runners/jobs/${initial.id}`, { headers });
  expect(complete.status()).toBe(200);
  return (await complete.json()) as RunnerJob;
}

async function fillCppCode(page: Page, source = cppSource) {
  const fallback = page.locator("[data-code-editor] #cpp-editor:visible");
  if (await fallback.count()) {
    await fallback.fill(source);
    return;
  }
  const editor = page.locator("[data-code-editor] .monaco-editor:visible").last();
  await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.evaluate(async (source) => navigator.clipboard.writeText(source), source);
  await editor.click();
  await page.keyboard.press("Control+A");
  await page.keyboard.press("Control+V");
}

async function capture(page: Page, journey: Journey, step: string) {
  const auditDirectory = process.env.HARD_VISUAL_AUDIT_DIR;
  expect(auditDirectory).toBeTruthy();
  const path = join(auditDirectory!, `${journey.name}-cpp-${step}-${journey.width}x${journey.height}.png`);
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth), `horizontal overflow at ${step}`).toBeTruthy();
  await page.screenshot({ path, fullPage: true });
  expect(existsSync(path)).toBe(true);
}

for (const journey of journeys) {
  test.describe(`C++ final E2E ${journey.name}`, () => {
    test.use({
      viewport: { width: journey.width, height: journey.height },
      extraHTTPHeaders: { "X-Hard-E2E-Client": journey.name },
    });

    test("uses the real C++ route, editor, runner, scoring, review and growth without private leakage", async ({ page }) => {
      test.setTimeout(180_000);
      await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);
      const lifecycle = await page.request.get("/api/_e2e/lifecycle");
      expect(lifecycle.status()).toBe(200);
      expect(await lifecycle.json()).toMatchObject({ lifespan: "started", application_count: 3 });

      await page.goto("/course/cpp");
      await expect(page.getByRole("heading", { name: "课程：cpp", exact: true })).toBeVisible();
      await expect(page.getByText("C++ 入门与语言基础", { exact: true })).toBeVisible();
      await expect(page.getByText("C++ 工具、实例、测验与结业", { exact: true })).toBeVisible();
      await capture(page, journey, "course");

      await page.getByRole("link", { name: "C++ 教程总览", exact: true }).click();
      await expect(page.getByRole("heading", { name: "C++ 教程总览", exact: true }).first()).toBeVisible();
      await page.locator("#lesson-note").fill(`Task 54 ${journey.name} C++ note`);
      await page.getByRole("button", { name: "保存笔记", exact: true }).click();
      await expect(page.getByText("已同步", { exact: true })).toBeVisible();
      await capture(page, journey, "lesson");

      await page.goto("/assessment/cpp-foundations-tutorial");
      await page.getByRole("button", { name: /^知识题(?:\s|$)/ }).first().click();
      await page.getByRole("radio", { name: "静态类型、编译执行并支持多种编程范式的通用语言", exact: true }).check();
      await page.getByRole("button", { name: "提交答案", exact: true }).click();
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();

      await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
      const workspace = page.locator("[data-code-editor]");
      await expect(workspace).toHaveAttribute("data-language", "cpp");
      await expect(workspace.getByText("C++ 代码编辑器", { exact: true })).toBeVisible();
      await expect(workspace).not.toContainText("Java 代码编辑器");
      await expect(workspace).not.toContainText("Python 代码编辑器");
      await expect(workspace).not.toContainText("C# 代码编辑器");
      await expect(workspace.locator(".monaco-editor:visible, textarea:visible")).toHaveCount(1);
      await fillCppCode(page);
      const submitted = page.waitForResponse((response) =>
        response.url().includes("/api/runners/submissions") && response.request().method() === "POST",
      );
      await page.getByRole("button", { name: "运行代码", exact: true }).click();
      const submissionResponse = await submitted;
      const payload = submissionResponse.request().postDataJSON() as { source_code: string };
      expect(payload.source_code.replaceAll("\r\n", "\n")).toBe(cppSource);
      const submission = submissionResponse.json() as Promise<RunnerJob>;
      const jobId = (await submission).id;
      await expect.poll(async () => {
        const response = await page.request.get(`/api/runners/jobs/${jobId}`, {
          headers: { "X-Hard-E2E-Client": journey.name },
        });
        expect(response.status()).toBe(200);
        return ((await response.json()) as RunnerJob).status;
      }, { timeout: 60_000 }).toBe("succeeded");
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
      await expect(pythonWorkspace).not.toContainText("C++ 代码编辑器");

      await page.goto("/assessment/java-foundations-tutorial");
      await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
      const javaWorkspace = page.locator("[data-code-editor]");
      await expect(javaWorkspace).toHaveAttribute("data-language", "java");
      await expect(javaWorkspace.getByText("Java 代码编辑器", { exact: true })).toBeVisible();
      await expect(javaWorkspace).not.toContainText("C++ 代码编辑器");

      await page.goto("/assessment/cpp-capstone-quiz");
      await page.getByRole("button", { name: /^挑战(?:\s|$)/ }).click();
      const challengeSource = `#include <iostream>
#include <iomanip>
#include <vector>
#include <thread>
int main() {
 int n; if (!(std::cin >> n) || n < 1 || n > 100) return 1;
 std::vector<int> scores(n);
 for (int &v : scores) if (!(std::cin >> v) || v < 0 || v > 100) return 1;
 std::string extra; if (std::cin >> extra) return 1;
 int sums[2] = {}, passes[2] = {};
 auto work = [&](int slot, int begin, int end) { for (int i=begin; i<end; ++i) { sums[slot]+=scores[i]; passes[slot]+=scores[i]>=60; } };
 std::thread a(work,0,0,n/2), b(work,1,n/2,n); a.join(); b.join();
 std::cout << "count=" << n << " pass=" << passes[0]+passes[1] << " average=" << std::fixed << std::setprecision(2) << double(sums[0]+sums[1])/n << std::endl;
 return 0;
}
`;
      await fillCppCode(page, challengeSource);
      const challengeScoring = page.waitForResponse(response => response.url().includes("/api/assessment/attempts") && response.request().method() === "POST");
      await page.getByRole("button", { name: "运行代码", exact: true }).click();
      const challengeScore = await challengeScoring;
      expect(challengeScore.status()).toBe(200);
      const challengeAssessment = await challengeScore.json();
      expect(challengeAssessment).toMatchObject({ question_score: 100 });
      if (journey.name === "mobile") await page.getByRole("button", { name: "结果", exact: true }).click();
      await expect(page.getByRole("heading", { name: "运行状态：运行完成", exact: true })).toBeVisible();
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();
      await capture(page, journey, "capstone-challenge");

      const beforePlacement = await (await page.request.get("/api/progress/summary")).json();
      expect(beforePlacement.unlocked_lessons.cpp).not.toContain("cpp-capstone-quiz");
      for (const value of [84.99, 85]) {
        const placement = await page.request.post("/api/assessment/placement", {
          headers: { "Idempotency-Key": `phase-g-placement-${journey.name}-${value}` },
          data: { language: "cpp", module_id: "cpp-capstone", score: value },
        });
        expect(placement.status()).toBe(200);
        expect(await placement.json()).toMatchObject({ validated: value === 85, experience_candidate: false });
        // 分级测试语义：达标分数验证模块课时（写入模块级掌握度快照），
        // 但 capstone 模块的前置（cpp-algorithms-concurrency）未完成时，unlocked 列表保持关闭。
        const summary = await (await page.request.get("/api/progress/summary")).json();
        expect(summary.unlocked_lessons.cpp.includes("cpp-capstone-quiz")).toBe(false);
      }
      const prerequisitePlacement = await page.request.post("/api/assessment/placement", {
        headers: { "Idempotency-Key": `release-cpp-prerequisite-${journey.name}` },
        data: { language: "cpp", module_id: "cpp-algorithms-concurrency", score: 85 },
      });
      expect(prerequisitePlacement.status()).toBe(200);
      expect(await prerequisitePlacement.json()).toMatchObject({ validated: true });
      const unlockedAfterPrerequisite = await (await page.request.get("/api/progress/summary")).json();
      expect(unlockedAfterPrerequisite.unlocked_lessons.cpp).toContain("cpp-capstone-quiz");
      await page.goto("/lesson/cpp-capstone-quiz");
      await expect(page.getByRole("heading", { name: "C++ 测验与路线结业", exact: true }).first()).toBeVisible();

      await capture(page, journey, "capstone-lesson");
      const fullScoreWeaknesses = await page.request.get("/api/growth/weaknesses");
      expect(fullScoreWeaknesses.status()).toBe(200);
      const baselineWeaknesses = (await fullScoreWeaknesses.json()).items as Array<{ concept_id: string; score: number; lesson_id: string }>;
      expect(baselineWeaknesses.filter(item => item.lesson_id.startsWith("cpp"))).toEqual([]);
      const previousScores = new Map(baselineWeaknesses.map(item => [item.concept_id, item.score]));
      await page.goto("/assessment/cpp-foundations-tutorial");
      await page.getByRole("button", { name: /^知识题(?:\s|$)/ }).first().click();
      await page.getByRole("radio", { name: "只能编写网页脚本的解释型语言", exact: true }).check();
      await page.getByRole("button", { name: "提交答案", exact: true }).click();
      await expect(page.getByText("本题得分：0", { exact: true })).toBeVisible();
      const queueBefore = await (await page.request.get("/api/review/queue")).json();
      const reviewItem = queueBefore.items.find((item: { exercise_id: string }) => item.exercise_id === "cpp-foundations-tutorial-k01");
      expect(reviewItem).toBeTruthy();
      await page.goto("/review");
      await expect(page.getByRole("heading", { name: "复习中心", exact: true })).toBeVisible();
      await expect(page.locator("[data-review-queue]")).toBeVisible();
      await capture(page, journey, "review-before");
      const reviewSaved = page.waitForResponse(response => response.url().endsWith(`/api/review/items/${reviewItem.id}`) && response.request().method() === "POST");
      await page.locator(`[data-review-item-id="${reviewItem.id}"]`).getByRole("button", { name: "掌握（80）", exact: true }).click();
      const reviewResponse = await reviewSaved;
      expect(reviewResponse.status()).toBe(200);
      const updatedReview = await reviewResponse.json();
      expect(updatedReview).toMatchObject({ id: reviewItem.id, score: 80, interval_days: 3 });
      await expect(page.getByText(`下次复习：${updatedReview.due_on}`, { exact: true })).toBeVisible();
      const queueAfter = await (await page.request.get("/api/review/queue")).json();
      expect(queueAfter.items.some((item: { id: number }) => item.id === reviewItem.id)).toBe(false);
      await capture(page, journey, "review-updated");
      writeFileSync(join(process.env.HARD_VISUAL_AUDIT_DIR!, `${journey.name}-contracts.json`), JSON.stringify({ viewport: journey, basic_runner_job_id: jobId, challenge: challengeAssessment, placement_before: beforePlacement.unlocked_lessons.cpp, placement_after: (await (await page.request.get("/api/progress/summary")).json()).unlocked_lessons.cpp, review_before: reviewItem, review_after: updatedReview, review_queue_after: queueAfter }, null, 2));

      await page.goto("/growth");
      await expect(page.getByRole("heading", { name: "成长报告", exact: true })).toBeVisible();
      await expect(page.locator('[data-mastery-record][data-scope-id^="cpp"]').first()).toBeVisible();
      const weaknesses = await page.request.get("/api/growth/weaknesses");
      expect(weaknesses.status()).toBe(200);
      const weaknessItems = (await weaknesses.json()).items;
      const tutorialWeaknesses = weaknessItems.filter((item: { exercise_id: string }) => item.exercise_id === "cpp-foundations-tutorial-k01");
      expect(tutorialWeaknesses.length).toBeGreaterThan(0);
      for (const item of tutorialWeaknesses) expect(item).toMatchObject({ score: (previousScores.get(item.concept_id) ?? 0) + 4, lesson_id: "cpp-foundations-tutorial", exercise_id: "cpp-foundations-tutorial-k01" });
      await capture(page, journey, "growth");
      if (journey.name === "mobile") {
        expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();
      }
    });
  });
}

test("real C++ API keeps runner results private and contract-accurate", async ({ page }) => {
  test.setTimeout(180_000);
  await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);

  const job = await runCppSubmission(
    page,
    "cpp-foundations-tutorial",
    "cpp-foundations-tutorial-c01",
    cppSource,
    "api-greeting",
  );
  expect(job.status).toBe("succeeded");
  const payload = JSON.stringify(job);
  expect(payload).not.toContain("reference_solution");
  expect(payload).not.toContain("hidden_");
  expect(payload).not.toContain("runner-work");
  expect(payload).not.toContain("D:\\projects");

  const broken = await runCppSubmission(
    page,
    "cpp-foundations-tutorial",
    "cpp-foundations-tutorial-c01",
    "int main() { return does_not_compile; }",
    "api-compile-failed",
  );
  expect(broken.status).toBe("failed");
  const failedPayload = JSON.stringify(broken);
  expect(failedPayload).not.toContain("reference_solution");
  expect(failedPayload).not.toContain("hidden_");
  expect(failedPayload).not.toContain("runner-work");

  const looping = await runCppSubmission(
    page,
    "cpp-foundations-tutorial",
    "cpp-foundations-tutorial-c01",
    "int main() { for (;;) {} }",
    "api-run-timeout",
  );
  expect(looping.status).toBe("timed_out");
  expect(looping.result?.status).toBe("timed_out");
  expect(looping.result?.diagnostics).toContain("运行超时。");
  const timedOutPayload = JSON.stringify(looping);
  expect(timedOutPayload).not.toContain("reference_solution");
  expect(timedOutPayload).not.toContain("hidden_");
  expect(timedOutPayload).not.toContain("runner-work");

  const flooding = await runCppSubmission(
    page,
    "cpp-foundations-tutorial",
    "cpp-foundations-tutorial-c01",
    "#include <cstdio>\nint main() { for (int i = 0; i < 4000; i++) std::printf(\"0123456789012345678\\n\"); return 0; }\n",
    "api-output-overflow",
  );
  expect(flooding.status).toBe("output_overflow");
  expect(flooding.result?.status).toBe("output_overflow");
  const overflowPayload = JSON.stringify(flooding);
  expect(overflowPayload).not.toContain("reference_solution");
  expect(overflowPayload).not.toContain("hidden_");
  expect(overflowPayload).not.toContain("runner-work");
});
