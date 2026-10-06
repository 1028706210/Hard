import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

if (process.env.VITEST) {
  const [
    { mount },
    { createMemoryHistory },
    { describe, expect, it, vi },
    { default: App },
    { requestJson, ApiClientError },
    { createHardRouter },
  ] = await Promise.all([
    import("@vue/test-utils"),
    import("vue-router"),
    import("vitest"),
    import("../src/App.vue"),
    import("../src/api/client"),
    import("../src/app/router"),
  ]);

  const destinations = [
    ["/", "知识星图主页"],
    ["/course/python", "课程：python"],
    ["/lesson/python-basics", "课时：python-basics"],
    ["/review", "复习中心"],
    ["/search", "搜索"],
    ["/compare", "跨语言对照"],
    ["/growth", "成长报告"],
    ["/settings", "设置"],
  ] as const;

  async function mountAt(path: string) {
    const router = createHardRouter(createMemoryHistory());
    await router.push(path);
    await router.isReady();
    return { router, wrapper: mount(App, { global: { plugins: [router] } }) };
  }

  describe("application shell", () => {
    it.each(destinations)("makes %s accessible", async (path, heading) => {
      const { wrapper } = await mountAt(path);

      expect(wrapper.text()).toContain(heading);
    });

    it("redirects an unknown route to the home destination", async () => {
      const { router, wrapper } = await mountAt("/unknown-route");

      expect(router.currentRoute.value.path).toBe("/");
      expect(wrapper.text()).toContain("知识星图主页");
    });

    it("uses language and lesson route parameters", async () => {
      const course = await mountAt("/course/java");
      const lesson = await mountAt("/lesson/java-basics");

      expect(course.wrapper.text()).toContain("课程：java");
      expect(lesson.wrapper.text()).toContain("课时：java-basics");
    });

    it("preserves the API error body", async () => {
      const body = {
        error: {
          code: "not_found",
          message: "未找到请求的资源。",
          details: { lesson_id: "missing" },
          request_id: "request-42",
        },
      };
      const fetchImpl = vi.fn().mockResolvedValue(
        new Response(JSON.stringify(body), {
          status: 404,
          headers: { "content-type": "application/json" },
        }),
      );

      await expect(requestJson("/api/v1/lessons/missing", {}, fetchImpl)).rejects.toEqual(
        new ApiClientError(404, body),
      );
    });

    it("retries a failed code draft without secure-context UUID support while retaining its source", async () => {
      localStorage.setItem("hard:offline-drafts", JSON.stringify([{
        kind: "code",
        url: "/api/runners/submissions",
        method: "POST",
        body: { lesson_id: "l1", exercise_id: "l1-c01", source_code: "print('keep me')" },
        idempotencyKey: "failed-draft",
        state: "failed_runner",
        runnerJobId: "old-job",
        scoreIdempotencyKey: "old-score-key",
        failureReason: "timed_out",
      }]));
      vi.stubGlobal("crypto", {});
      vi.spyOn(Math, "random").mockReturnValueOnce(0.11).mockReturnValueOnce(0.22);
      const { wrapper } = await mountAt("/");

      expect(wrapper.get('[aria-label="离线运行失败"]').attributes("role")).toBe("alert");
      const retry = wrapper.get('[aria-label="离线运行失败"] button');
      await retry.trigger("click");

      const [draft] = JSON.parse(localStorage.getItem("hard:offline-drafts") ?? "[]") as Array<Record<string, unknown>>;
      expect(draft).toMatchObject({
        idempotencyKey: expect.stringMatching(/^failed-draft:/),
        state: "pending_runner",
        body: { lesson_id: "l1", exercise_id: "l1-c01", source_code: "print('keep me')" },
      });
      expect(String(draft.idempotencyKey)).not.toBe("failed-draft");
      expect(String(draft.idempotencyKey).length).toBeLessThanOrEqual(128);
      expect(draft.runnerJobId).toBeUndefined();
      expect(draft.scoreIdempotencyKey).toBeUndefined();
      expect(draft.failureReason).toBeUndefined();
      const firstRetryKey = String(draft.idempotencyKey);
      wrapper.unmount();
      localStorage.setItem("hard:offline-drafts", JSON.stringify([{
        kind: "code", url: "/api/runners/submissions", method: "POST", body: { source_code: "print('keep me')" }, idempotencyKey: "failed-draft", state: "failed_runner", failureReason: "timed_out",
      }]));
      const second = await mountAt("/");
      await second.wrapper.get('[aria-label="离线运行失败"] button').trigger("click");
      const [secondDraft] = JSON.parse(localStorage.getItem("hard:offline-drafts") ?? "[]") as Array<Record<string, unknown>>;
      expect(String(secondDraft.idempotencyKey)).not.toBe(firstRetryKey);
      vi.unstubAllGlobals();
    });
  });
} else {
  const { expect, test } = await import("@playwright/test");

  test("the web application has an executable test entry", () => {
    const entryPoint = fileURLToPath(new URL("../index.html", import.meta.url));

    expect(existsSync(entryPoint)).toBe(true);
  });
}
