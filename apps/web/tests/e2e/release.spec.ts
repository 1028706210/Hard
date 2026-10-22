import { expect, test, type Page } from "@playwright/test";
import { existsSync, writeFileSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

type Journey = { name: "desktop" | "mobile"; width: number; height: number };
const journeys: readonly Journey[] = [
  { name: "desktop", width: 1440, height: 1024 },
  { name: "mobile", width: 390, height: 844 },
];

const pythonSource = `import sys
name = sys.stdin.read().strip()
if name == "__invalid__" or (name and not name.isalpha()):
    raise ValueError("name must contain letters only")
print(f"Hello, {name or 'World'}!")`;

const javaSource = `import java.nio.charset.StandardCharsets;

public class Main {
    public static void main(String[] args) throws Exception {
        String value = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        if (value.isEmpty()) System.exit(1);
        System.out.println("Hello, " + value);
    }
}`;

const csharpSource = `var value = Console.ReadLine() ?? "";
value = value.Trim();
Console.WriteLine(value.Length == 0 ? "empty" : value.ToUpperInvariant());
`;

const cppSource = `#include <iostream>
#include <string>

int main() {
    std::string name;
    std::getline(std::cin, name);
    std::cout << "Hello, " << name << "!" << std::endl;
    return 0;
}
`;

type RunnerJob = {
  id: string;
  status: "queued" | "running" | "succeeded" | "failed" | "cancelled" | "timed_out" | "output_overflow" | "rejected" | "tool_missing";
  result?: unknown;
};

const realRuns = [
  { language: "python", lessonId: "python-foundations-hello-world", editorSelector: "#python-editor", source: pythonSource },
  { language: "java", lessonId: "java-foundations-tutorial", editorSelector: "#java-editor", source: javaSource },
  { language: "csharp", lessonId: "csharp-foundations-tutorial", editorSelector: "#csharp-editor", source: csharpSource },
  { language: "cpp", lessonId: "cpp-foundations-tutorial", editorSelector: "#cpp-editor", source: cppSource },
] as const;

async function fillLanguageCode(page: Page, language: string, editorSelector: string, source: string) {
  const fallback = page.locator(`[data-code-editor] ${editorSelector}:visible`);
  if (await fallback.count()) {
    await fallback.fill(source);
    return;
  }
  const editor = page.locator("[data-code-editor] .monaco-editor:visible").last();
  await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.evaluate(async (text) => navigator.clipboard.writeText(text), source);
  await editor.click();
  await page.keyboard.press("Control+A");
  await page.keyboard.press("Control+V");
}

async function runRealExercise(page: Page, journey: Journey, run: (typeof realRuns)[number]) {
  await page.goto(`/assessment/${run.lessonId}`);
  await page.getByRole("button", { name: /^代码题(?:\s|$)/ }).click();
  const workspace = page.locator("[data-code-editor]");
  await expect(workspace).toHaveAttribute("data-language", run.language);
  await fillLanguageCode(page, run.language, run.editorSelector, run.source);
  await page.getByRole("button", { name: "运行代码", exact: true }).click();
  if (journey.name === "mobile") await page.getByRole("button", { name: "结果", exact: true }).click();
  await expect(page.getByRole("heading", { name: "运行状态：运行完成", exact: true })).toBeVisible({ timeout: 45_000 });
  await expect(page.getByText(run.language === "java" ? "公开测试：2 / 2 通过" : "公开测试：1 / 1 通过", { exact: true })).toBeVisible();
  await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();
  expect(await page.content()).not.toContain("reference_solution");
  expect(await page.content()).not.toContain("hidden_");
  await capture(page, journey, `run-${run.language}`);
}

async function capture(page: Page, journey: Journey, step: string) {
  const auditDirectory = process.env.HARD_VISUAL_AUDIT_DIR;
  if (!auditDirectory) return;
  const path = join(auditDirectory, `${journey.name}-release-${step}-${journey.width}x${journey.height}.png`);
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth), `horizontal overflow at ${step}`).toBeTruthy();
  if (step === "restore") {
    expect(await page.locator(".settings-page").evaluate((element) =>
      [...element.querySelectorAll("*")].every((child) => child.getBoundingClientRect().right <= window.innerWidth),
    ), "settings content must remain inside the viewport even when the document clips overflow").toBeTruthy();
  }
  await page.screenshot({ path, fullPage: true });
  expect(existsSync(path)).toBe(true);
}

for (const journey of journeys) {
  test.describe(`Release journey ${journey.name}`, () => {
    test.use({
      viewport: { width: journey.width, height: journey.height },
      extraHTTPHeaders: { "X-Hard-E2E-Client": journey.name },
    });

    test("covers route entries, real runs, review, search, compare, growth and backup restore", async ({ page }) => {
      test.setTimeout(journey.name === "desktop" ? 300_000 : 240_000);
      await expect.poll(async () => (await page.request.get("/api/v1/health/live")).status(), { timeout: 15_000 }).toBe(200);

      // 四路线入口
      await page.goto("/");
      await expect(page.locator("[data-map-world]")).toHaveCount(4);
      await capture(page, journey, "home-start");
      for (const language of ["python", "java", "csharp", "cpp"]) {
        await page.goto(`/course/${language}`);
        await expect(page.getByRole("heading", { name: `课程：${language}`, exact: true })).toBeVisible();
      }
      await capture(page, journey, "courses");

      if (journey.name === "desktop") {
        // 每语言一道真实运行题
        const runnerResults: Record<string, string> = {};
        for (const run of realRuns) {
          await runRealExercise(page, journey, run);
          runnerResults[run.language] = "succeeded";
        }
        writeFileSync(join(process.env.HARD_VISUAL_AUDIT_DIR ?? ".tool-cache", `${journey.name}-runner-results.json`), JSON.stringify(runnerResults, null, 2));

        // 笔记与搜索
        await page.goto("/lesson/python-foundations-hello-world");
        await page.locator("#lesson-note").fill(`Release ${journey.name} 真实笔记`);
        await page.getByRole("button", { name: "保存笔记", exact: true }).click();
        await expect(page.getByText("已同步", { exact: true })).toBeVisible();
        await page.getByRole("button", { name: "收藏课时", exact: true }).click();
        await expect(page.getByRole("button", { name: "取消收藏", exact: true })).toBeVisible();
        await page.goto("/search");
        await page.getByRole("searchbox", { name: "搜索课程内容" }).fill(`Release ${journey.name} 真实笔记`);
        await page.getByRole("button", { name: "搜索", exact: true }).click();
        await expect(page.locator(".result-snippet").first()).toContainText(new RegExp(`\\[Release\\].*\\[${journey.name}\\]`));

        // 复习：答错进入队列并完成一次评级
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
        await capture(page, journey, "review");
        await page.getByRole("button", { name: "掌握（80）", exact: true }).first().click();
        await expect(page.getByText(/下次复习：/)).toBeVisible();

        // 跨语言对照
        await page.goto("/compare");
        const variables = page.locator("[data-concept-card='variables']");
        await expect(variables).toBeVisible();
        await expect(variables.locator("[data-language]")).toHaveCount(4);
        await page.locator("[data-concept-filter]").fill("pointers");
        await expect(page.locator("[data-concept-card]")).toHaveCount(1);
        await expect(page.locator("[data-concept-card='pointers']").locator("[data-language='python'] [data-missing-slot]")).toContainText("缺失");
        await capture(page, journey, "compare");
      }

      // 正确作答一道知识题，产生掌握度记录
      await page.goto("/assessment/python-foundations-hello-world");
      await page.getByRole("button", { name: /^知识题(?:\s|$)/ }).nth(1).click();
      await page.getByRole("radio", { name: "文件顶部", exact: true }).check();
      await page.getByRole("button", { name: "提交答案", exact: true }).click();
      await expect(page.getByText("本题得分：100", { exact: true })).toBeVisible();

      // 成长报告
      await page.goto("/growth");
      await expect(page.getByRole("heading", { name: "成长报告", exact: true })).toBeVisible();
      await expect(page.locator("[data-mastery-record]").first()).toContainText(/模块|课程/);
      await expect(page.locator("[data-activity-date]")).toHaveCount(90);
      const activityResponse = await page.request.get("/api/growth/summary");
      expect(activityResponse.status()).toBe(200);
      const activity = await activityResponse.json() as { activity_end_date: string; activity_days: Array<{ date: string; completed_exercises: number }> };
      await expect(page.locator(`[data-activity-date="${activity.activity_end_date}"]`)).toHaveCount(1);
      for (const day of activity.activity_days) {
        await expect(page.locator(`[data-activity-date="${day.date}"]`)).toHaveAttribute("aria-label", new RegExp(`${day.completed_exercises} 道已完成练习`));
      }
      await capture(page, journey, "growth");

      // 备份导出与实际恢复
      const beforeExport = await (await page.request.get("/api/progress/summary")).json();
      await page.goto("/settings");
      await page.getByRole("button", { name: "创建导出包", exact: true }).click();
      const archive = page.locator("[data-export-name]");
      await expect(archive).toContainText("hard-export-");
      const archiveName = (await archive.textContent())?.replace("已保存至 exports/", "").trim();
      expect(archiveName).toMatch(/^hard-export-[a-f0-9]{24}\.zip$/);
      const archiveBytes = await readFile(
        join(process.cwd(), "..", "..", ".tool-cache", `live-e2e-${process.env.HARD_E2E_RUN_ID}`, journey.name, "exports", archiveName!),
      );
      const changed = await page.request.patch("/api/progress/lessons/python-foundations-hello-world", {
        headers: { "Idempotency-Key": `release-${journey.name}-after-export-position` },
        data: { position: 999, time_spent_seconds: 0 },
      });
      expect(changed.status()).toBe(200);
      await page.locator('input[type="file"]').setInputFiles({ name: archiveName!, mimeType: "application/zip", buffer: archiveBytes });
      await page.getByRole("button", { name: "安全导入", exact: true }).click();
      await expect(page.getByText(/导入完成，内容版本：/)).toBeVisible();
      const afterImport = await (await page.request.get("/api/progress/summary")).json();
      expect(afterImport.continue_learning.position).toBe(beforeExport.continue_learning.position);
      await capture(page, journey, "restore");

      if (journey.name === "mobile") {
        // 手机离线草稿恢复：断网提交 → 恢复联网自动补交
        await page.goto("/assessment/python-foundations-hello-world");
        await page.getByRole("button", { name: /^知识题(?:\s|$)/ }).first().click();
        await page.getByRole("radio", { name: "input", exact: true }).check();
        await page.context().setOffline(true);
        await page.getByRole("button", { name: "提交答案", exact: true }).click();
        await expect(page.getByText("答案尚未保存，已保留为离线草稿。请恢复连接后重试。")).toBeVisible();
        await expect
          .poll(async () => await page.evaluate(() => globalThis.localStorage.getItem("hard:offline-drafts") ?? ""))
          .toContain("answer");
        await page.context().setOffline(false);
        await expect
          .poll(async () => await page.evaluate(() => globalThis.localStorage.getItem("hard:offline-drafts")), { timeout: 15_000 })
          .toBe(null);
        await expect.poll(async () => {
          const queue = await (await page.request.get("/api/review/queue")).json();
          return queue.items.some((item: { exercise_id: string }) => item.exercise_id === "python-foundations-hello-world-k01");
        }, { timeout: 15_000 }).toBe(true);
        await capture(page, journey, "draft-restored");
      }
    });
  });
}
