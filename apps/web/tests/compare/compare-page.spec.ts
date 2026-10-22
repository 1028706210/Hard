import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import { createMemoryHistory, createRouter } from "vue-router";

import ComparePage from "../../src/features/compare/ComparePage.vue";

const mounted: ReturnType<typeof mount>[] = [];
afterEach(() => {
  mounted.splice(0).forEach(wrapper => wrapper.unmount());
  vi.unstubAllGlobals();
});

async function renderComparison(path = "/compare") {
  const router = createRouter({ history: createMemoryHistory(), routes: [
    { path: "/compare", component: ComparePage },
    { path: "/lesson/:lessonId", component: { template: "<p>课时内容</p>" } },
  ] });
  await router.push(path);
  await router.isReady();
  const wrapper = mount({ template: "<RouterView />" }, { global: { plugins: [router] } });
  mounted.push(wrapper);
  await flushPromises();
  return { wrapper, router };
}

function response(body: unknown) {
  return new Response(JSON.stringify(body), { headers: { "content-type": "application/json" } });
}

function slot(
  overrides: Partial<Record<string, unknown>> = {},
) {
  return {
    status: "available",
    summary: "语言内对该概念的一句话说明。",
    difference: "与其他语言的语义差异。",
    code: "value = 1\n",
    lesson_id: "python-foundations-variables",
    lesson_title: "变量",
    note: null,
    ...overrides,
  };
}

const payload = {
  content_version: "abc123",
  concepts: [
    {
      id: "variables",
      name: "变量",
      description: "保存可变值的命名位置。",
      slots: {
        python: slot({
          code: "value = 1\n<img src=x onerror=\"window.__pwned = true\">\n",
        }),
        java: slot({ lesson_id: "java-foundations-variable-types", lesson_title: "变量类型" }),
        csharp: slot({
          status: "missing",
          summary: "",
          difference: "",
          code: null,
          lesson_id: null,
          lesson_title: null,
          note: "C# 路线内没有可对照的标注课时。",
        }),
        cpp: slot({
          status: "missing",
          summary: "",
          difference: "",
          code: null,
          lesson_id: null,
          lesson_title: null,
          note: "C++ 路线内没有可对照的标注课时。",
        }),
      },
    },
    {
      id: "loops",
      name: "循环",
      description: "重复执行代码块的结构。",
      slots: {
        python: slot({ lesson_id: "python-flow-collections-loops", lesson_title: "循环" }),
        java: slot({ lesson_id: "java-foundations-loops", lesson_title: "循环" }),
        csharp: slot({ lesson_id: "csharp-foundations-loops", lesson_title: "循环" }),
        cpp: slot({ lesson_id: "cpp-foundations-loops", lesson_title: "循环" }),
      },
    },
  ],
};

function stubComparisonFetch() {
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url === "/api/compare/concepts") return response(payload);
    throw new Error(`unexpected ${url}`);
  }));
}

function stubPagedComparisonFetch() {
  vi.stubGlobal("fetch", vi.fn(async () => response({ concepts: Array.from({ length: 9 }, (_, index) => ({ ...payload.concepts[0], id: `concept-${index}`, name: `概念 ${index}` })) })));
}

describe("compare page", () => {
  it("pages through the full catalog and returns to the first page when filtering", async () => {
    stubPagedComparisonFetch();
    const { wrapper } = await renderComparison();
    await vi.waitFor(() => expect(wrapper.findAll("[data-concept-card]")).toHaveLength(4));
    await wrapper.get("[data-next-concepts]").trigger("click");
    await flushPromises();
    expect(wrapper.find("[data-concept-card='concept-4']").exists()).toBe(true);
    await wrapper.get("[data-next-concepts]").trigger("click");
    await flushPromises();
    expect(wrapper.findAll("[data-concept-card]")).toHaveLength(1);
    expect(wrapper.find("[data-concept-card='concept-8']").exists()).toBe(true);
    await wrapper.get("[data-concept-filter]").setValue("concept-0");
    await flushPromises();
    expect(wrapper.find("[data-concept-card='concept-0']").exists()).toBe(true);
    await wrapper.get("[data-concept-filter]").setValue("missing");
    await flushPromises();
    expect(wrapper.find("[data-empty-state]").exists()).toBe(true);
    expect(wrapper.findAll("[data-concept-card]")).toHaveLength(0);
  });

  it("restores the filtered concept after returning from a lesson", async () => {
    stubComparisonFetch();
    const { wrapper, router } = await renderComparison();
    await wrapper.get("[data-concept-filter]").setValue("loops");
    await flushPromises();
    await router.push(wrapper.get("[data-concept-card='loops'] [data-language='python'] a").attributes("href")!);
    expect(wrapper.find("[data-concept-filter]").exists()).toBe(false);

    router.back();
    await vi.waitFor(() => expect(wrapper.find("[data-concept-filter]").exists()).toBe(true));
    expect((wrapper.get("[data-concept-filter]").element as HTMLInputElement).value).toBe("loops");
    expect(wrapper.findAll("[data-concept-card]")).toHaveLength(1);
    expect(wrapper.find("[data-concept-card='loops']").exists()).toBe(true);
  });

  it("restores the selected page after returning from a lesson", async () => {
    stubPagedComparisonFetch();
    const { wrapper, router } = await renderComparison();
    await wrapper.get("[data-next-concepts]").trigger("click");
    await flushPromises();
    await router.push(wrapper.get("[data-concept-card='concept-4'] [data-language='python'] a").attributes("href")!);

    router.back();
    await vi.waitFor(() => expect(wrapper.find("[data-concept-filter]").exists()).toBe(true));
    expect(wrapper.find("[data-concept-card='concept-4']").exists()).toBe(true);
    expect(wrapper.find("[data-concept-card='concept-0']").exists()).toBe(false);
    expect(wrapper.text()).toContain("第 2 / 3 页");
  });

  it("reads the filter and page from the URL and resets only the page when filtering", async () => {
    stubPagedComparisonFetch();
    const { wrapper, router } = await renderComparison("/compare?filter=concept&page=2&source=lesson");
    expect((wrapper.get("[data-concept-filter]").element as HTMLInputElement).value).toBe("concept");
    expect(wrapper.find("[data-concept-card='concept-4']").exists()).toBe(true);

    await wrapper.get("[data-concept-filter]").setValue("concept-0");
    await flushPromises();
    expect(wrapper.find("[data-concept-card='concept-0']").exists()).toBe(true);
    expect(router.currentRoute.value.query).toEqual({ filter: "concept-0", source: "lesson" });

    await wrapper.get("[data-concept-filter]").setValue("");
    await flushPromises();
    expect(router.currentRoute.value.query).toEqual({ source: "lesson" });
  });

  it.each(["0", "-1", "1.5", "invalid", "999999999999999999999", "2&page=3"])("uses the first page for invalid page query %s", async page => {
    stubPagedComparisonFetch();
    const { wrapper } = await renderComparison(`/compare?page=${page}`);
    expect(wrapper.find("[data-concept-card='concept-0']").exists()).toBe(true);
    expect(wrapper.findAll("[data-concept-card]")).toHaveLength(4);
  });

  it("bounds a bookmarked page to the available filtered results", async () => {
    stubComparisonFetch();
    const { wrapper } = await renderComparison("/compare?filter=loops&page=99");
    expect(wrapper.find("[data-concept-card='loops']").exists()).toBe(true);
    expect(wrapper.findAll("[data-concept-card]")).toHaveLength(1);
  });
  it("renders four language slots per concept with lesson links and explicit missing slots", async () => {
    stubComparisonFetch();

    const { wrapper } = await renderComparison();
    await vi.waitFor(() => expect(wrapper.find("[data-concept-card='variables']").exists()).toBe(true));

    const cards = wrapper.findAll("[data-concept-card]");
    expect(cards).toHaveLength(2);
    const variables = wrapper.find("[data-concept-card='variables']");
    expect(variables.find("[data-language='python'] a").attributes("href")).toBe("/lesson/python-foundations-variables");
    expect(variables.find("[data-language='python']").text()).toContain("与其他语言的语义差异。");
    expect(variables.find("[data-language='csharp']").text()).toContain("C# 路线内没有可对照的标注课时。");
    expect(variables.find("[data-language='cpp']").text()).toContain("缺失");
  });

  it("renders code examples as escaped text and never executes them as HTML", async () => {
    stubComparisonFetch();

    const { wrapper } = await renderComparison();
    await vi.waitFor(() => expect(wrapper.find("[data-concept-card='variables']").exists()).toBe(true));

    const pythonSlot = wrapper.find("[data-concept-card='variables'] [data-language='python']");
    const codeText = pythonSlot.find("pre code").text();
    expect(codeText).toContain('<img src=x onerror="window.__pwned = true">');
    expect(pythonSlot.find("img").exists()).toBe(false);
    expect((window as unknown as Record<string, unknown>).__pwned).toBeUndefined();
  });

  it("filters concepts by id or Chinese name", async () => {
    stubComparisonFetch();

    const { wrapper } = await renderComparison();
    await vi.waitFor(() => expect(wrapper.findAll("[data-concept-card]")).toHaveLength(2));

    await wrapper.find("[data-concept-filter]").setValue("循环");
    await flushPromises();
    expect(wrapper.findAll("[data-concept-card]")).toHaveLength(1);
    expect(wrapper.find("[data-concept-card='loops']").exists()).toBe(true);

    await wrapper.find("[data-concept-filter]").setValue("variables");
    await flushPromises();
    expect(wrapper.findAll("[data-concept-card]")).toHaveLength(1);
    expect(wrapper.find("[data-concept-card='variables']").exists()).toBe(true);
  });

  it("shows an explicit error instead of silently dropping content when the API fails", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("{}", { status: 500 })));

    const { wrapper } = await renderComparison();
    await vi.waitFor(() => expect(wrapper.find("[role='alert']").exists()).toBe(true));
    expect(wrapper.text()).toContain("无法读取");
  });

  it("shows an empty state when the catalog has no comparable concepts", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => response({ content_version: "abc", concepts: [] })));

    const { wrapper } = await renderComparison();
    await vi.waitFor(() => expect(wrapper.find("[data-empty-state]").exists()).toBe(true));
  });
});
