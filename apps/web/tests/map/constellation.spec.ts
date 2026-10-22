import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import { createMemoryHistory, createRouter } from "vue-router";
import HomeConstellations from "../../src/features/map/HomeConstellations.vue";
import ConstellationPage from "../../src/features/map/ConstellationPage.vue";
import { groupedConcepts, linkedLanguages, starPositions, type ChainConcept, type ChainCourse, type ConceptSlot } from "../../src/features/map/constellation";

const missing: ConceptSlot = { status: "missing", summary: "", difference: "", code: null, lesson_id: null, lesson_title: null, note: "尚未标注" };
const slot = (id: string): ConceptSlot => ({ ...missing, status: "available", lesson_id: id, lesson_title: id, summary: "变量的语言内语义", difference: "静态类型与动态绑定", code: "<script>unsafe()</script>" });
const concepts: ChainConcept[] = [
  { id: "variables", name: "变量", description: "保存可变值的命名位置", slots: { python: slot("py-vars"), java: slot("java-vars"), csharp: missing, cpp: slot("wrong-language") } },
  { id: "loops", name: "循环", description: "重复执行", slots: { python: slot("py-loops"), java: missing, csharp: missing, cpp: missing } },
];
const courses: ChainCourse[] = [
  { language: "python", modules: [{ id: "py-core", title: "基础", lessons: [{ id: "py-vars", title: "Python 变量" }, { id: "unmapped", title: "未标注课时" }, { id: "wrong-language", title: "仅 Python 课时" }] }, { id: "py-flow", title: "控制流", lessons: [{ id: "py-loops", title: "Python 循环" }] }] },
  { language: "java", modules: [{ id: "java-core", title: "Java 基础", lessons: [{ id: "java-vars", title: "Java 变量" }] }] },
];
async function render(home = false) {
  const payloads: Record<string, unknown> = {
    "/api/content/catalog": { courses }, "/api/compare/concepts": { concepts },
    "/api/progress/summary": { lesson_statuses: { "py-vars": "in_progress" } },
    "/api/growth/summary": { mastery: [] }, "/api/review/queue": { items: [] },
  };
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => new Response(JSON.stringify(payloads[String(input)]), { headers: { "content-type": "application/json" } }));
  vi.stubGlobal("fetch", fetchMock);
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: "/:pathMatch(.*)*", component: ConstellationPage }] });
  await router.push("/constellations");
  const wrapper = mount(ConstellationPage, { props: { home }, global: { plugins: [router] } });
  await flushPromises();
  return { wrapper, fetchMock };
}
afterEach(() => vi.unstubAllGlobals());
describe("knowledge constellations", () => {
  it("connects only available references in the matching language catalog", () => {
    expect(linkedLanguages(concepts[0], courses)).toEqual(["python", "java"]);
    expect(linkedLanguages(concepts[0], [])).toEqual([]);
  });
  it("keeps directory order continuous at the turn of each star-chain row", () => {
    const stars = starPositions(Array.from({ length: 9 }, (_, i) => ({ id: String(i), title: String(i) })));
    expect(stars.map(star => star.id)).toEqual(['0','1','2','3','4','5','6','7','8']);
    expect(new Set(stars.map(star => `${star.x},${star.y}`)).size).toBe(9);
    expect(stars.every(star => star.x >= 100 && star.x <= 860 && star.y >= 50)).toBe(true);
    expect(stars.slice(1).every((star, index) => Math.hypot(star.x - stars[index].x, star.y - stars[index].y) < 350)).toBe(true);
    expect(starPositions([])).toEqual([]);
  });
  it("loads bounded aggregates, shows saved progress and authored differences, and escapes examples", async () => {
    const { wrapper, fetchMock } = await render();
    expect(fetchMock).toHaveBeenCalledTimes(6);
    expect(wrapper.get('.selected-lesson [data-learning-state]').text()).toBe('学习中');
    expect(wrapper.findAll("[data-connection]")).toHaveLength(2);
    expect(wrapper.text()).toContain("静态类型与动态绑定");
    expect(wrapper.find("pre script").exists()).toBe(false);
    expect(wrapper.get("pre code").text()).toBe("<script>unsafe()</script>");
    expect(wrapper.findAll(".language-star:disabled")).toHaveLength(2);
    wrapper.unmount();
  });
  it("aligns selected concepts with their module and language without extra requests", async () => {
    const { wrapper, fetchMock } = await render();
    await wrapper.get('.chain-toolbar button:nth-child(2)').trigger("click");
    expect(wrapper.get('.chain-panel h2').text()).toBe("Java 基础");
    expect(wrapper.get('.selected-lesson a').attributes('href')).toBe('/lesson/java-vars');
    await wrapper.get('.chain-toolbar button:first-child').trigger("click");
    await wrapper.get('.resonance .concept-chips button:nth-child(2)').trigger("click");
    expect(wrapper.get('.chain-panel h2').text()).toBe("控制流");
    expect(wrapper.get('.selected-lesson a').attributes('href')).toBe('/lesson/py-loops');
    expect(fetchMock).toHaveBeenCalledTimes(6);
    wrapper.unmount();
  });
  it("does not invent connections for unmapped lessons and supports empty searches", async () => {
    const { wrapper } = await render();
    await wrapper.get('.star-node:nth-of-type(2)').trigger('click');
    expect(wrapper.text()).toContain('本课尚无已标注的跨语言对照');
    expect(wrapper.find('[data-connection]').exists()).toBe(false);
    await wrapper.get('input').setValue('does-not-exist');
    expect(wrapper.text()).toContain('没有匹配的概念');
    wrapper.unmount();
  });
});


describe("homepage constellation interactions", () => {
  it("keeps the homepage and expanded module motion controls in sync", async () => {
    const { wrapper } = await render(true);
    await wrapper.get('.module-disclosure').trigger('click');
    await wrapper.get('.motion-toggle').trigger('click');
    expect(wrapper.get('.chain-motion-toggle').attributes('aria-pressed')).toBe('true');
    expect(wrapper.get('.chain-motion-toggle').text()).toBe('开启星链动效');
    await wrapper.get('.chain-motion-toggle').trigger('click');
    expect(wrapper.get('.motion-toggle').attributes('aria-pressed')).toBe('false');
    wrapper.unmount();
  });
  it("keeps missing and wrong-language references disabled and emits a real concept", async () => {
    const wrapper = mount(HomeConstellations, { props: { courses, concepts, selected: concepts[0] } });
    expect(wrapper.findAll('[data-connection]')).toHaveLength(2);
    expect(wrapper.get('[aria-label="C++ · 变量，暂无标注课时"]').attributes('disabled')).toBeDefined();
    await wrapper.get('[aria-label="Python · 变量"]').trigger('click');
    expect(wrapper.emitted('concept')).toEqual([['variables', 'python']]);
    await wrapper.get('[data-map-world=java] .language-heading').trigger('click');
    expect(wrapper.emitted('course')).toEqual([['java']]);
    await wrapper.get('.motion-toggle').trigger('click');
    expect(wrapper.get('.motion-toggle').attributes('aria-pressed')).toBe('true');
    wrapper.unmount();
  });
  it("brings a non-core selected concept into the map without inventing other language links", () => {
    const wrapper = mount(HomeConstellations, { props: { courses, concepts, selected: concepts[1] } });
    expect(wrapper.get('[aria-label="Python · 循环"]').attributes('aria-pressed')).toBe('true');
    expect(wrapper.findAll('[data-connection]')).toHaveLength(1);
    expect(wrapper.get('[data-connection]').attributes('data-connection')).toBe('python');
    wrapper.unmount();
  });
});


it("groups actual concepts once and retains a selected non-featured concept", () => {
  const extra = { ...concepts[0], id: 'pointers', name: '指针' };
  const groups = groupedConcepts([...concepts, extra], 'pointers');
  expect(groups.map(group => group.title)).toEqual(['基础语法', '函数与组织', '数据与对象']);
  expect(groups.flatMap(group => group.members).map(concept => concept.id).sort()).toEqual(['loops', 'pointers', 'variables']);
  expect(groups[2].displayed.map(concept => concept.id)).toContain('pointers');
  expect(groups.flatMap(group => group.displayed).some(concept => concept.id === 'parameters')).toBe(false);
});
