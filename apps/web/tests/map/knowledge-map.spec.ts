import { createMemoryHistory } from "vue-router";
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import App from "../../src/App.vue";
import { createHardRouter } from "../../src/app/router";
import { buildMapSnapshot, refreshMapSnapshot, useMapStore } from "../../src/features/map/map.store";


async function mountHome() {
  const router = createHardRouter(createMemoryHistory());
  await router.push("/");
  await router.isReady();
  return mount(App, { global: { plugins: [router] } });
}


describe("knowledge map", () => {
  it("distinguishes saved lesson progress, mastery and due reviews without promoting a visit to mastery", () => {
    const lessons = ["new", "reading", "done", "mastered", "review"].map(id => ({ id, title: id }));
    const state = buildMapSnapshot(
      { courses: [{ language: "python", modules: [{ lessons }] }] },
      { lesson_statuses: { reading: "in_progress", done: "completed", mastered: "completed", review: "validated" } },
      { mastery: [{ scope_type: "lesson", scope_id: "mastered", score: 90 }, { scope_type: "lesson", scope_id: "review", score: 100 }] },
      { items: [{ lesson_id: "review" }] },
    );
    expect(state.lessons.new).toMatchObject({ status: "not_started", label: "未学习" });
    expect(state.lessons.reading).toMatchObject({ status: "in_progress", label: "学习中" });
    expect(state.lessons.done).toMatchObject({ status: "completed", label: "已学完" });
    expect(state.lessons.mastered).toMatchObject({ status: "mastered", label: "已掌握" });
    expect(state.lessons.review).toMatchObject({ status: "due_review", label: "待复习" });
    expect(state.mastery).toBe("38%");
    expect(state.languages.python.status).toBe("in_progress");
  });

  it("shows a retryable error instead of fallback learning metrics when a critical API fails", async () => {
    await refreshMapSnapshot(vi.fn().mockRejectedValue(new Error("offline")) as unknown as typeof fetch);

    expect(useMapStore().loadState).toBe("error");
    expect(useMapStore().error).toContain("重试");
    expect(useMapStore().level).toBe("");
    expect(useMapStore().mastery).toBe("");
  });

  it("shows a loading state instead of static learning metrics before the critical APIs resolve", async () => {
    const wrapper = await mountHome();

    expect(wrapper.get('[role="status"]').text()).toContain("正在读取学习概览");
    expect(wrapper.text()).not.toContain("Lv. 1");
    expect(wrapper.text()).not.toContain("未开始");
  });

  it("does not expose navigation actions until real learning data is ready", async () => {
    const wrapper = await mountHome();

    expect(wrapper.find('[data-continue-learning]').exists()).toBe(false);
    expect(wrapper.find('[data-mobile-route]').exists()).toBe(false);
  });

  it.each([
    ["without content", [], null, [], "unavailable", "尚无课程内容", "尚无继续学习课时"],
    ["before starting", [{ language: "python", modules: [{ prerequisites: [], lessons: [{ id: "python-foundations-hello-world", title: "Hello World" }] }] }], null, [], "not_started", "未开始", "开始学习 · Hello World"],
    ["after progress", [{ language: "python", modules: [{ prerequisites: [], lessons: [{ id: "python-foundations-hello-world", title: "Hello World" }] }] }], { course_id: "python", lesson_id: "python-foundations-hello-world", position: 4 }, [], "in_progress", "学习中", "Hello World"],
    ["after course mastery", [{ language: "python", modules: [{ prerequisites: [], lessons: [{ id: "python-foundations-hello-world", title: "Hello World" }] }] }], null, [{ scope_type: "course", scope_id: "python", score: 85 }], "mastered", "已掌握", "开始学习 · Hello World"],
    ["when its first module is gated", [{ language: "python", modules: [{ prerequisites: ["python-prerequisite"], lessons: [{ id: "python-foundations-hello-world", title: "Hello World" }] }] }], null, [], "locked", "待前置", "开始学习 · Hello World"],
  ] as const)("derives %s from real catalog, progress, and mastery", (_caseName, courses, continuing, mastery, status, label, continueTitle) => {
    const snapshot = buildMapSnapshot(
      { courses },
      { daily_goal: {}, continue_learning: continuing, current_level: 1, streak_days: 0 },
      { level: 1, streak_days: 0, mastery },
      { items: [] },
    );

    expect(snapshot.languages.python).toMatchObject({ status, label });
    expect(snapshot.continueLessonTitle).toBe(continueTitle);
  });

  it("uses the persisted unlock result instead of treating a course as enterable by default", () => {
    const snapshot = buildMapSnapshot(
      { courses: [{ language: "python", modules: [{ prerequisites: [], lessons: [{ id: "python-foundations-hello-world", title: "Hello World" }] }] }] },
      { daily_goal: {}, continue_learning: null, current_level: 1, streak_days: 0, unlocked_lessons: { python: [] } },
      { level: 1, streak_days: 0, mastery: [] },
      { items: [] },
    );

    expect(snapshot.languages.python).toMatchObject({ status: "locked", label: "待前置" });
    expect(snapshot.continueLessonId).toBe("");
  });
});
