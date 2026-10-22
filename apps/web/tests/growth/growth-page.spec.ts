import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import GrowthPage from "../../src/features/growth/GrowthPage.vue";


function response(body: unknown) {
  return new Response(JSON.stringify(body), { headers: { "content-type": "application/json" } });
}

describe("growth page", () => {
  it("keeps every mastery record reachable and combines scope, language and text filters", async () => {
    const mastery = Array.from({ length: 14 }, (_, index) => ({ scope_type: "lesson", scope_id: `python-lesson-${index}`, score: index }));
    mastery.push({ scope_type: "module", scope_id: "java-foundations", score: 90 });
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      if (String(input) === "/api/growth/summary") return response({ total_experience: 0, level: 1, next_level_remaining: 100, streak_days: 0, badges: [], mastery });
      if (String(input) === "/api/content/catalog") return response({ courses: [] });
      if (String(input) === "/api/compare/concepts") return response({ concepts: [] });
      return response({ items: [] });
    }));
    const wrapper = mount(GrowthPage);
    await vi.waitFor(() => expect(wrapper.findAll("[data-mastery-record]")).toHaveLength(12));
    await wrapper.get("[data-more-mastery]").trigger("click");
    expect(wrapper.findAll("[data-mastery-record]")).toHaveLength(15);
    await wrapper.get("[data-mastery-language]").setValue("java");
    await wrapper.get("[data-mastery-scope]").setValue("module");
    expect(wrapper.findAll("[data-mastery-record]")).toHaveLength(1);
    expect(wrapper.get("[data-mastery-record]").attributes("data-scope-id")).toBe("java-foundations");
    await wrapper.get("[data-mastery-search]").setValue("missing");
    expect(wrapper.findAll("[data-mastery-record]")).toHaveLength(0);
    await wrapper.get("[data-reset-mastery]").trigger("click");
    expect(wrapper.findAll("[data-mastery-record]")).toHaveLength(12);
  });
  it("renders actual activity and empty dates without inventing completed exercises", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      if (String(input) === "/api/growth/summary") return response({ total_experience: 0, level: 1, next_level_remaining: 100, streak_days: 1, badges: [], mastery: [], activity_start_date: "2026-07-04", activity_end_date: "2026-10-01", activity_days: [{ date: "2026-07-04", completed_exercises: 4, time_spent_seconds: 120 }, { date: "2026-10-01", completed_exercises: 0, time_spent_seconds: 0 }] });
      if (String(input) === "/api/content/catalog") return response({ courses: [] });
      if (String(input) === "/api/compare/concepts") return response({ concepts: [] });
      return response({ items: [] });
    }));
    const wrapper = mount(GrowthPage);
    await vi.waitFor(() => expect(wrapper.findAll("[data-activity-date]")).toHaveLength(90));
    expect(wrapper.get('[data-activity-date="2026-07-04"]').attributes("data-level")).toBe("4");
    expect(wrapper.get('[data-activity-date="2026-07-04"]').attributes("aria-label")).toContain("4 道已完成练习");
    expect(wrapper.get('[data-activity-date="2026-07-05"]').attributes("data-level")).toBe("0");
    expect(wrapper.get('[data-activity-date="2026-10-01"]').attributes("aria-label")).toContain("0 道已完成练习");
    expect(wrapper.find('[data-activity-date="2026-10-02"]').exists()).toBe(false);
  });
  it("resolves catalog names without changing scores or links", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      if (String(input) === "/api/content/catalog") return response({ courses: [{ language: "python", modules: [{ id: "python-foundations", title: "Python 基础", lessons: [{ id: "python-foundations-hello-world", title: "第一次输出" }] }] }] });
      if (String(input) === "/api/compare/concepts") return response({ concepts: [{ id: "python-output", name: "文本输出" }] });
      if (String(input) === "/api/growth/summary") return response({ total_experience: 120, level: 2, next_level_remaining: 80, streak_days: 3, badges: [], mastery: [{ scope_type: "lesson", scope_id: "python-foundations-hello-world", score: 80 }, { scope_type: "module", scope_id: "python-foundations", score: 70 }] });
      if (String(input) === "/api/growth/weaknesses") return response({ items: [{ concept_id: "python-output", score: 4, lesson_id: "python-foundations-hello-world", exercise_id: "python-foundations-hello-world-c01" }] });
      return response({ items: [] });
    }));
    const wrapper = mount(GrowthPage);
    await vi.waitFor(() => expect(wrapper.text()).toContain("课时 · 第一次输出"));
    expect(wrapper.text()).toContain("模块 · Python 基础");
    expect(wrapper.get("meter").attributes("value")).toBe("80");
    expect(wrapper.get("[data-weakness-link]").text()).toBe("文本输出");
    expect(wrapper.get("[data-weakness-link]").attributes("href")).toBe("/assessment/python-foundations-hello-world");
    expect(wrapper.text()).toContain("第一次输出 · c01");
  });
  it("shows only returned growth data, an explicit empty heatmap, and escaped source history", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      if (String(input) === "/api/growth/summary") return response({ total_experience: 120, level: 2, current_level_progress: 20, next_level_remaining: 80, streak_days: 3, badges: ["first_lesson"], mastery: [{ scope_type: "lesson", scope_id: "python-foundations-hello-world", score: 80 }], new_badges: [], route_completion: [] });
      if (String(input) === "/api/growth/history") return response({ items: [{ id: "s1", exercise_id: "python-foundations-hello-world-c01", language: "python", source_code: "<script>code</script>", normalized_result: { score: 80 }, score: 80, duration_ms: 4, created_at: "2026-08-25", diff: "<script>diff</script>" }] });
      if (String(input) === "/api/growth/weaknesses") return response({ items: [{ concept_id: "python-output", score: 4, lesson_id: "python-foundations-hello-world", exercise_id: "python-foundations-hello-world-c01" }] });
      throw new Error("unexpected request");
    }));

    const wrapper = mount(GrowthPage);
    await vi.waitFor(() => expect(wrapper.text()).toContain("120 XP"));
    expect(wrapper.get(".mastery li").text()).toContain("课时 · python-foundations-hello-world");
    expect(wrapper.get(".mastery li").text()).toContain("80%");
    expect(wrapper.get(".badges").text()).toContain("完成第一课");
    expect(wrapper.text()).toContain("热力图数据尚不可用");
    expect(wrapper.get('[data-weakness-link]').attributes("href")).toBe("/assessment/python-foundations-hello-world");
    expect(wrapper.html()).toContain("&lt;script&gt;code&lt;/script&gt;");
    expect(wrapper.html()).not.toContain("<script>code</script>");
    expect(wrapper.find("pre").attributes("data-plain-text")).toBe("source");
  });
});
