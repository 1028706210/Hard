import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import GrowthPage from "../../src/features/growth/GrowthPage.vue";


function response(body: unknown) {
  return new Response(JSON.stringify(body), { headers: { "content-type": "application/json" } });
}

describe("growth page", () => {
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
    expect(wrapper.text()).toContain("热力图数据尚不可用");
    expect(wrapper.get('[data-weakness-link]').attributes("href")).toBe("/assessment/python-foundations-hello-world");
    expect(wrapper.html()).toContain("&lt;script&gt;code&lt;/script&gt;");
    expect(wrapper.html()).not.toContain("<script>code</script>");
    expect(wrapper.find("pre").attributes("data-plain-text")).toBe("source");
  });
});
