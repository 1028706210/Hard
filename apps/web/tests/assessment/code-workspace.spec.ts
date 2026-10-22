import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { describe, expect, it, vi } from "vitest";

const monaco = vi.hoisted(() => {
  const model = {};
  const editor = { getValue: () => "", setValue: vi.fn(), getModel: () => model, updateOptions: vi.fn(), onDidChangeModelContent: () => ({ dispose: vi.fn() }), dispose: vi.fn() };
  return { create: vi.fn(() => editor), setModelLanguage: vi.fn(), model, instance: editor };
});
const assessment = vi.hoisted(() => ({ state: { lesson: null as Record<string, unknown> | null, run: null, runState: "idle", assessment: null, error: "", loadState: "ready", runningJobId: "" }, loadLesson: vi.fn(), selectExercise: vi.fn(), submitKnowledge: vi.fn(), runCode: vi.fn(), cancelRun: vi.fn() }));

vi.mock("monaco-editor", () => ({ editor: monaco }));
vi.mock("../../src/features/assessment/assessment.store", () => ({ assessmentStore: assessment }));

import CodeWorkspace from "../../src/features/assessment/CodeWorkspace.vue";
import AssessmentPage from "../../src/features/assessment/AssessmentPage.vue";

describe("code workspace language", () => {
  it("does not reset the current exercise when a superseded lesson load is discarded", async () => {
    let finishOld!: (value: null) => void;
    const currentLesson = { id: "current", language: "python", exercises: [
      { id: "first", type: "knowledge", prompt: "第一题", choices: [{ id: "a", text: "A" }] },
      { id: "second", type: "knowledge", prompt: "第二题", choices: [{ id: "b", text: "B" }] },
    ] };
    assessment.state.lesson = currentLesson;
    assessment.loadLesson.mockImplementationOnce(() => new Promise(resolve => { finishOld = resolve; })).mockResolvedValueOnce(currentLesson);
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: "/assessment/:lessonId", component: AssessmentPage }] });
    await router.push("/assessment/old");
    const wrapper = mount(AssessmentPage, { global: { plugins: [router] } });
    await router.push("/assessment/current");
    await flushPromises();
    await wrapper.findAll(".exercise-nav button")[1]!.trigger("click");
    expect(wrapper.get(".knowledge-question > p").text()).toBe("第二题");
    finishOld(null);
    await flushPromises();
    expect(wrapper.get(".knowledge-question > p").text()).toBe("第二题");
    expect(wrapper.findAll(".exercise-nav button")[1]!.attributes("aria-pressed")).toBe("true");
    wrapper.unmount();
  });

  it("selects feedback by exercise and preserves knowledge answers across a code exercise", async () => {
    const choice = { id: "a", text: "答案 A" };
    assessment.state.lesson = { id: "switching", language: "python", exercises: [
      { id: "first", type: "knowledge", prompt: "第一题", choices: [choice] },
      { id: "second", type: "knowledge", prompt: "第二题", choices: [choice] },
      { id: "code", type: "code", prompt: "代码题", choices: [], starter_code: "", visible_tests: [], experience_points: 1 },
    ] };
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: "/assessment/:lessonId", component: AssessmentPage }] });
    await router.push("/assessment/switching");
    const wrapper = mount(AssessmentPage, { global: { plugins: [router] } });
    await flushPromises();
    await wrapper.get('input[type="radio"]').setValue();
    await wrapper.findAll(".knowledge-question__hints button")[0]!.trigger("click");
    const navigation = wrapper.findAll(".exercise-nav button");
    await navigation[1]!.trigger("click");
    expect(assessment.selectExercise).toHaveBeenLastCalledWith("second");
    expect(wrapper.findAll("input:checked")).toHaveLength(0);
    await navigation[2]!.trigger("click");
    await navigation[0]!.trigger("click");
    expect(assessment.selectExercise).toHaveBeenLastCalledWith("first");
    expect(wrapper.findAll("input:checked")).toHaveLength(1);
    expect(wrapper.findAll(".knowledge-question__hints button")[0]!.attributes("aria-pressed")).toBe("true");
    wrapper.unmount();
  });

  it("keeps the existing Python Monaco semantics", async () => {
    const wrapper = mount(CodeWorkspace, { props: { modelValue: "print('ok')", language: "python", running: false } });
    await flushPromises();

    expect(wrapper.get("[data-code-editor]").attributes("data-language")).toBe("python");
    expect(wrapper.get("label").text()).toBe("Python 代码编辑器");
    expect(monaco.create).toHaveBeenCalledWith(expect.anything(), expect.objectContaining({ language: "python", ariaLabel: "Python 代码编辑器" }));
  });

  it("updates Monaco model language and accessibility label when the lesson language changes", async () => {
    const wrapper = mount(CodeWorkspace, { props: { modelValue: "class Main {}", language: "java", running: false } });
    await flushPromises();

    expect(wrapper.get("[data-code-editor]").attributes("data-language")).toBe("java");
    expect(wrapper.get("label").text()).toBe("Java 代码编辑器");
    expect(monaco.create).toHaveBeenLastCalledWith(expect.anything(), expect.objectContaining({ language: "java", ariaLabel: "Java 代码编辑器" }));
    await wrapper.setProps({ language: "python" });
    expect(monaco.setModelLanguage).toHaveBeenCalledWith(monaco.model, "python");
    expect(monaco.instance.updateOptions).toHaveBeenCalledWith({ ariaLabel: "Python 代码编辑器" });
  });

  it("uses explicit C# Monaco and accessibility semantics", async () => {
    const wrapper = mount(CodeWorkspace, { props: { modelValue: "class Program {}", language: "csharp", running: false } });
    await flushPromises();

    expect(wrapper.get("[data-code-editor]").attributes("data-language")).toBe("csharp");
    expect(wrapper.get("label").text()).toBe("C# 代码编辑器");
    expect(monaco.create).toHaveBeenLastCalledWith(expect.anything(), expect.objectContaining({ language: "csharp", ariaLabel: "C# 代码编辑器" }));
  });

  it("uses explicit C++ Monaco and accessibility semantics", async () => {
    const wrapper = mount(CodeWorkspace, { props: { modelValue: "#include <iostream>", language: "cpp", running: false } });
    await flushPromises();

    expect(wrapper.get("[data-code-editor]").attributes("data-language")).toBe("cpp");
    expect(wrapper.get("label").text()).toBe("C++ 代码编辑器");
    expect(monaco.create).toHaveBeenLastCalledWith(expect.anything(), expect.objectContaining({ language: "cpp", ariaLabel: "C++ 代码编辑器" }));
  });

  it("maps unsupported languages to plaintext instead of Python", async () => {
    const wrapper = mount(CodeWorkspace, { props: { modelValue: "puts 'hello'", language: "ruby", running: false } });
    await flushPromises();

    expect(wrapper.get("[data-code-editor]").attributes("data-language")).toBe("plaintext");
    expect(wrapper.get("label").text()).toBe("纯文本代码编辑器");
    expect(monaco.create).toHaveBeenLastCalledWith(expect.anything(), expect.objectContaining({ language: "plaintext", ariaLabel: "纯文本代码编辑器" }));
  });

  it("updates model and accessibility semantics across C#, C++, Python, and unknown languages", async () => {
    const wrapper = mount(CodeWorkspace, { props: { modelValue: "class Program {}", language: "java", running: false } });
    await flushPromises();

    await wrapper.setProps({ language: "csharp" });
    await wrapper.setProps({ language: "cpp" });
    await wrapper.setProps({ language: "python" });
    await wrapper.setProps({ language: "unsupported" });

    expect(monaco.setModelLanguage).toHaveBeenCalledWith(monaco.model, "csharp");
    expect(monaco.setModelLanguage).toHaveBeenCalledWith(monaco.model, "cpp");
    expect(monaco.setModelLanguage).toHaveBeenCalledWith(monaco.model, "python");
    expect(monaco.setModelLanguage).toHaveBeenCalledWith(monaco.model, "plaintext");
    expect(monaco.instance.updateOptions).toHaveBeenCalledWith({ ariaLabel: "C# 代码编辑器" });
    expect(monaco.instance.updateOptions).toHaveBeenCalledWith({ ariaLabel: "C++ 代码编辑器" });
    expect(monaco.instance.updateOptions).toHaveBeenCalledWith({ ariaLabel: "Python 代码编辑器" });
    expect(monaco.instance.updateOptions).toHaveBeenCalledWith({ ariaLabel: "纯文本代码编辑器" });
  });

  it("passes a C++ lesson language from the assessment page to the workspace", async () => {
    assessment.state.lesson = { id: "cpp-basics", language: "cpp", exercises: [{ id: "cpp-code", type: "code", prompt: "C++ 代码题", choices: [], starter_code: "#include <iostream>", visible_tests: [], experience_points: 1 }] };
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: "/assessment/:lessonId", component: AssessmentPage }] });
    await router.push("/assessment/cpp-basics");
    await router.isReady();
    const wrapper = mount(AssessmentPage, { global: { plugins: [router] } });
    await flushPromises();

    expect(wrapper.get("[data-code-editor]").attributes("data-language")).toBe("cpp");
  });

  it("passes a Java lesson language from the assessment page to the workspace", async () => {
    assessment.state.lesson = { id: "java-basics", language: "java", exercises: [{ id: "java-code", type: "code", prompt: "Java 代码题", choices: [], starter_code: "class Main {}", visible_tests: [], experience_points: 1 }] };
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: "/assessment/:lessonId", component: AssessmentPage }] });
    await router.push("/assessment/java-basics");
    await router.isReady();
    const wrapper = mount(AssessmentPage, { global: { plugins: [router] } });
    await flushPromises();

    expect(wrapper.get("[data-code-editor]").attributes("data-language")).toBe("java");
  });

  it("passes a C# lesson language unchanged from the assessment page", async () => {
    assessment.state.lesson = { id: "csharp-basics", language: "csharp", exercises: [{ id: "csharp-code", type: "code", prompt: "C# 代码题", choices: [], starter_code: "class Program {}", visible_tests: [], experience_points: 1 }] };
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: "/assessment/:lessonId", component: AssessmentPage }] });
    await router.push("/assessment/csharp-basics");
    await router.isReady();
    const wrapper = mount(AssessmentPage, { global: { plugins: [router] } });
    await flushPromises();

    expect(wrapper.get("[data-code-editor]").attributes("data-language")).toBe("csharp");
  });

});
