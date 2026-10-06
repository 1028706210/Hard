import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import ComparePage from "../../src/features/compare/ComparePage.vue";


function response(body: unknown) {
  return new Response(JSON.stringify(body), { headers: { "content-type": "application/json" } });
}

describe("compare page", () => {
  it("aligns current content by concept ID and marks unavailable language content explicitly", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/content/catalog") return response({ courses: [{ language: "python", modules: [{ lessons: [{ id: "python-foundations-hello-world" }] }] }] });
      if (url === "/api/content/lessons/python-foundations-hello-world") return response({ id: "python-foundations-hello-world", language: "python", title: "Hello World", concepts: ["python-output"] });
      throw new Error(`unexpected ${url}`);
    }));

    const wrapper = mount(ComparePage);
    await vi.waitFor(() => expect(wrapper.text()).toContain("python-output"));
    expect(wrapper.find('[data-language="python"]').text()).toContain("Hello World");
    expect(wrapper.find('[data-language="java"]').text()).toContain("尚无内容");
    expect(wrapper.findAll('[data-language]')).toHaveLength(4);
  });
});
