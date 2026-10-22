import { mount, RouterLinkStub } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import SearchPage from "../../src/features/search/SearchPage.vue";


describe("search page", () => {
  it("keeps the submitted query with its results and explains an empty query without requesting", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ results: [{ source_type: "lesson", language: "python", lesson_id: "hello", title: "输出", snippet: "print", anchor: "" }] }), { headers: { "content-type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    const wrapper = mount(SearchPage, { global: { stubs: { RouterLink: RouterLinkStub } } });
    await wrapper.get("form").trigger("submit.prevent");
    expect(fetchMock).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain("请输入关键词");
    await wrapper.get("input").setValue("print");
    await wrapper.get("form").trigger("submit.prevent");
    await vi.waitFor(() => expect(wrapper.find("[data-search-summary]").text()).toContain("print"));
    await wrapper.get("input").setValue("loop");
    expect(wrapper.get("[data-search-summary]").text()).toContain("print");
    expect(wrapper.get("[data-search-summary]").text()).not.toContain("loop");
  });
  it("submits a query, locates a lesson, and renders snippets as text", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      expect(String(input)).toBe("/api/search?q=print");
      return new Response(JSON.stringify({ results: [{ source_type: "lesson", language: "python", lesson_id: "python-foundations-hello-world", title: "Hello World", snippet: "<script>print</script>", anchor: "output" }] }), { headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", fetchMock);

    const wrapper = mount(SearchPage, { global: { stubs: { RouterLink: RouterLinkStub } } });
    await wrapper.get('input[aria-label="搜索课程内容"]').setValue("print");
    await wrapper.get("form").trigger("submit.prevent");
    await vi.waitFor(() => expect(wrapper.get("a").attributes("href")).toBe("/lesson/python-foundations-hello-world#output"));
    expect(wrapper.html()).toContain("&lt;script&gt;print&lt;/script&gt;");
    expect(wrapper.html()).not.toContain("<script>print</script>");
  });
});
