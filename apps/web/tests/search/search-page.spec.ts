import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import SearchPage from "../../src/features/search/SearchPage.vue";


describe("search page", () => {
  it("submits a query, locates a lesson, and renders snippets as text", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      expect(String(input)).toBe("/api/search?q=print");
      return new Response(JSON.stringify({ results: [{ source_type: "lesson", language: "python", lesson_id: "python-foundations-hello-world", title: "Hello World", snippet: "<script>print</script>", anchor: "output" }] }), { headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", fetchMock);

    const wrapper = mount(SearchPage);
    await wrapper.get('input[aria-label="搜索课程内容"]').setValue("print");
    await wrapper.get("form").trigger("submit.prevent");
    await vi.waitFor(() => expect(wrapper.get("a").attributes("href")).toBe("/lesson/python-foundations-hello-world#output"));
    expect(wrapper.html()).toContain("&lt;script&gt;print&lt;/script&gt;");
    expect(wrapper.html()).not.toContain("<script>print</script>");
  });
});
