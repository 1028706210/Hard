import { createMemoryHistory } from "vue-router";
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import App from "../../src/App.vue";
import { createHardRouter } from "../../src/app/router";
import { languageWorlds } from "../../src/features/map/map-layout";
import { buildMapSnapshot } from "../../src/features/map/map.store";


async function mountHome() {
  const router = createHardRouter(createMemoryHistory());
  await router.push("/");
  await router.isReady();
  return mount(App, { global: { plugins: [router] } });
}


describe("knowledge map", () => {
  it("keeps all four language routes visible and enterable around the continue-learning action", async () => {
    const wrapper = await mountHome();
    const worlds = wrapper.get(".orbital-map").findAll('[data-map-world]');

    expect(worlds.map((world) => world.attributes("data-map-world"))).toEqual(languageWorlds.map((world) => world.id));
    expect(wrapper.find('[data-continue-learning]').exists()).toBe(false);
    expect(wrapper.text()).toContain("尚无继续学习课时");
    expect(wrapper.get('[data-map-world="python"]').text()).toContain("尚无课程内容");
    expect(wrapper.get('[data-map-world="java"]').text()).toContain("尚无课程内容");
    expect(wrapper.get('[data-map-world="csharp"]').text()).toContain("尚无课程内容");
    expect(wrapper.get('[data-map-world="cpp"]').text()).toContain("尚无课程内容");
    expect(wrapper.get('[data-map-world="python"]').classes()).toContain("map-world--unavailable");
    expect(wrapper.get('[data-route-node="cpp"] .mobile-route__marker').classes()).toContain("mobile-route__marker--unavailable");
  });

  it("renders a separate touch-operable vertical route instead of shrinking the orbital canvas", async () => {
    const wrapper = await mountHome();
    const mobileRoute = wrapper.get('[data-mobile-route]');

    expect(mobileRoute.findAll('[data-route-node]')).toHaveLength(4);
    expect(mobileRoute.findAll("a").map((link) => link.attributes("href"))).toEqual(
      languageWorlds.map((world) => `/course/${world.id}`),
    );
    expect(wrapper.find(".orbital-map").exists()).toBe(true);
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
