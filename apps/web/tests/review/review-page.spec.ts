import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import ReviewPage from "../../src/features/review/ReviewPage.vue";


function response(body: unknown) {
  return new Response(JSON.stringify(body), { headers: { "content-type": "application/json" } });
}

describe("review page", () => {
  it("keeps scheduled reviews separate from ordinary weak-answer links and scores only queue items", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === "/api/review/queue") return response({ items: [{ id: 7, concept_id: "python-output", lesson_id: "python-foundations-hello-world", exercise_id: "python-foundations-hello-world-k01", due_on: "2026-08-25", interval_days: 1, last_score: 40 }] });
      if (url === "/api/growth/weaknesses") return response({ items: [{ concept_id: "python-output", score: 4, lesson_id: "python-foundations-hello-world", exercise_id: "python-foundations-hello-world-k01" }] });
      if (url === "/api/review/items/7") {
        expect(init?.headers).toMatchObject({ "Idempotency-Key": expect.any(String) });
        expect(init?.body).toBe(JSON.stringify({ score: 80 }));
        return response({ id: 7, score: 80, interval_days: 3, due_on: "2026-08-28", experience_candidate: false });
      }
      throw new Error(`unexpected ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const wrapper = mount(ReviewPage);
    await vi.waitFor(() => expect(wrapper.find('[data-review-queue="true"]').text()).toContain("python-output"));
    expect(wrapper.text()).toContain("普通错题浏览");
    expect(wrapper.find('[data-review-queue="true"]').text()).toContain("python-output");
    expect(wrapper.find('[data-wrong-answer-browser="true"] a').attributes("href")).toBe("/assessment/python-foundations-hello-world");

    await wrapper.get('[data-review-score="80"]').trigger("click");
    await vi.waitFor(() => expect(wrapper.text()).toContain("下次复习：2026-08-28"));
  });

  it("fails closed to empty sections when a late refresh has no item arrays", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => response({})));

    const wrapper = mount(ReviewPage);
    await vi.waitFor(() => expect(wrapper.find('[data-review-queue="true"]').text()).toContain("当前没有到期复习"));
    expect(wrapper.find('[data-wrong-answer-browser="true"]').text()).toContain("还没有普通错题线索");
  });
});
