import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import KnowledgeQuestion from "../../src/features/assessment/KnowledgeQuestion.vue";
import CodeExercise from "../../src/features/assessment/CodeExercise.vue";
import RunResult from "../../src/features/assessment/RunResult.vue";
import { loadEditorDraft, saveEditorDraft } from "../../src/features/assessment/editor-drafts";


describe("assessment components", () => {
  it("keeps answers and hint choices independent when moving between knowledge exercises", async () => {
    const exercise = { id: "first", type: "knowledge" as const, prompt: "第一题", choices: [{ id: "a", text: "选项 A" }, { id: "b", text: "选项 B" }] };
    const question = mount(KnowledgeQuestion, { props: { exercise } });
    await question.get('input[value="a"]').setValue();
    await question.findAll("button")[0]!.trigger("click");
    await question.setProps({ exercise: { ...exercise, id: "second", prompt: "第二题" } });
    expect(question.findAll('input:checked')).toHaveLength(0);
    expect(question.get(".knowledge-question__submit").attributes("disabled")).toBeDefined();
    expect(question.findAll('button[aria-pressed="true"]')).toHaveLength(0);
    await question.get('input[value="b"]').setValue();
    await question.findAll("button")[1]!.trigger("click");
    await question.setProps({ exercise });
    expect((question.get('input[value="a"]').element as HTMLInputElement).checked).toBe(true);
    expect(question.findAll("button")[0]!.attributes("aria-pressed")).toBe("true");
    await question.get(".knowledge-question__submit").trigger("click");
    expect(question.emitted("submit")?.[0]).toEqual(["a", "light"]);
  });

  it("distinguishes a pending run from a failed run in public feedback", () => {
    const result = mount(RunResult, { props: { result: { status: "queued", diagnostics: [], tests: null } } });
    expect(result.text()).toContain("排队中");
    expect(result.text()).not.toContain("运行未完成");
    expect(result.text()).not.toContain("重试");
  });

  it("gives changed code a new submission key while preserving a restored draft key", async () => {
    const values = new Map<string, string>();
    const storage = { getItem: (key: string) => values.get(key) ?? null, setItem: (key: string, value: string) => values.set(key, value), removeItem: (key: string) => values.delete(key) };
    saveEditorDraft(storage, "retry-lesson", "retry-code", "print(1)", "submitted-key");
    const props = { lessonId: "retry-lesson", language: "python", storage, running: false, result: null, exercise: { id: "retry-code", type: "code" as const, prompt: "代码题", choices: [], starter_code: "", visible_tests: [], experience_points: 1 } };
    const wrapper = mount(CodeExercise, { props });
    await wrapper.vm.$nextTick();
    expect(loadEditorDraft(storage, props.lessonId, props.exercise.id)?.idempotencyKey).toBe("submitted-key");
    await wrapper.get("textarea").setValue("print(2)");
    const changed = loadEditorDraft(storage, props.lessonId, props.exercise.id)!;
    expect(changed.sourceCode).toBe("print(2)");
    expect(changed.idempotencyKey).not.toBe("submitted-key");
    wrapper.unmount();
    const restored = mount(CodeExercise, { props });
    await restored.vm.$nextTick();
    expect(loadEditorDraft(storage, props.lessonId, props.exercise.id)?.idempotencyKey).toBe(changed.idempotencyKey);
    await restored.get("textarea").setValue("print(3)");
    expect(loadEditorDraft(storage, props.lessonId, props.exercise.id)?.idempotencyKey).not.toBe(changed.idempotencyKey);
    restored.unmount();
  });
  it("uses native radio semantics and arrow/space keyboard selection", async () => {
    const question = mount(KnowledgeQuestion, { attachTo: document.body, props: { exercise: { id: "k01", type: "knowledge", prompt: "题目", choices: [{ id: "a", text: "答案 A" }, { id: "b", text: "答案 B" }] } } });
    const radios = question.findAll('input[type="radio"]');

    expect(radios).toHaveLength(2);
    expect(question.find("fieldset").exists()).toBe(true);
    await radios[0]!.trigger("keydown", { key: "ArrowRight" });
    expect((radios[1]!.element as HTMLInputElement).checked).toBe(true);
    expect(document.activeElement).toBe(radios[1]!.element);
    await radios[0]!.trigger("keydown", { key: " " });
    expect((radios[0]!.element as HTMLInputElement).checked).toBe(true);
  });

  it("shows hint impact and only public runner feedback", async () => {
    const question = mount(KnowledgeQuestion, { props: { exercise: { id: "k01", type: "knowledge", prompt: "题目", choices: [{ id: "a", text: "答案" }] } } });
    await question.findAll("button")[0]!.trigger("click");
    expect(question.text()).toContain("轻提示后本题最高 85% 分");

    const result = mount(RunResult, { props: { result: { status: "failed", diagnostics: ["运行时错误"], tests: { visible_passed: 0, visible_total: 1 } } } });
    expect(result.text()).toContain("公开测试：0 / 1 通过");
    expect(result.text()).toContain("运行未完成");
  });

  it("restores and explicitly clears a local code draft", async () => {
    const values = new Map<string, string>();
    const storage = { getItem: (key: string) => values.get(key) ?? null, setItem: (key: string, value: string) => values.set(key, value), removeItem: (key: string) => values.delete(key) };
    saveEditorDraft(storage, "lesson-1", "code-1", "print('draft')", "draft-key");
    const wrapper = mount(CodeExercise, { props: { lessonId: "lesson-1", language: "python", storage, running: false, result: null, exercise: { id: "code-1", type: "code", prompt: "代码题", choices: [], starter_code: "print('starter')", visible_tests: [], experience_points: 1 } } });

    await wrapper.vm.$nextTick();
    expect((wrapper.get("textarea").element as HTMLTextAreaElement).value).toBe("print('draft')");
    expect(wrapper.text()).toContain("已恢复本地草稿");
    await wrapper.get('[data-clear-draft]').trigger("click");
    expect((wrapper.get("textarea").element as HTMLTextAreaElement).value).toBe("print('starter')");
    expect(loadEditorDraft(storage, "lesson-1", "code-1")).toBeNull();
  });

  it("forwards the lesson language to the fallback editor without changing draft behavior", async () => {
    const wrapper = mount(CodeExercise, { props: { lessonId: "java-lesson", language: "java", running: false, result: null, exercise: { id: "java-code", type: "code", prompt: "Java 代码题", choices: [], starter_code: "class Main {}", visible_tests: [], experience_points: 1 } } });

    await wrapper.vm.$nextTick();
    expect(wrapper.get("[data-code-editor]").attributes("data-language")).toBe("java");
    expect(wrapper.get("label").text()).toBe("Java 代码编辑器");
    expect(wrapper.get("textarea").attributes()).toMatchObject({ id: "java-editor", "aria-label": "Java 代码编辑器" });
    expect((wrapper.get("textarea").element as HTMLTextAreaElement).value).toBe("class Main {}");
  });

  it("keeps Java fallback run, cancel, and mobile result controls available", async () => {
    const wrapper = mount(CodeExercise, { props: { lessonId: "java-lesson", language: "java", running: false, result: null, exercise: { id: "java-code", type: "code", prompt: "Java 代码题", choices: [], starter_code: "class Main {}", visible_tests: [], experience_points: 1 } } });

    await wrapper.get(".code-workspace__editor button").trigger("click");
    expect(wrapper.emitted("run")?.[0]).toEqual(["class Main {}"]);
    await wrapper.setProps({ running: true });
    await wrapper.get(".code-workspace__editor button:last-child").trigger("click");
    expect(wrapper.emitted("cancel")).toHaveLength(1);
    await wrapper.findAll(".code-workspace__tabs button")[1]!.trigger("click");
    expect(wrapper.get("[data-code-editor]").classes()).toContain("code-workspace--result");
  });

  it("keeps C# and unsupported-language fallback ids and labels aligned with data-language", async () => {
    const csharp = mount(CodeExercise, { props: { lessonId: "csharp-lesson", language: "csharp", running: false, result: null, exercise: { id: "csharp-code", type: "code", prompt: "C# 代码题", choices: [], starter_code: "class Program {}", visible_tests: [], experience_points: 1 } } });
    const unknown = mount(CodeExercise, { props: { lessonId: "ruby-lesson", language: "ruby", running: false, result: null, exercise: { id: "ruby-code", type: "code", prompt: "不支持的代码题", choices: [], starter_code: "puts 'hello'", visible_tests: [], experience_points: 1 } } });

    await csharp.vm.$nextTick();
    await unknown.vm.$nextTick();
    expect(csharp.get("[data-code-editor]").attributes("data-language")).toBe("csharp");
    expect(csharp.get("textarea").attributes()).toMatchObject({ id: "csharp-editor", "aria-label": "C# 代码编辑器" });
    expect(unknown.get("[data-code-editor]").attributes("data-language")).toBe("plaintext");
    expect(unknown.get("textarea").attributes()).toMatchObject({ id: "plaintext-editor", "aria-label": "纯文本代码编辑器" });
  });

  it("keeps C++ fallback id and label aligned with data-language", async () => {
    const cpp = mount(CodeExercise, { props: { lessonId: "cpp-lesson", language: "cpp", running: false, result: null, exercise: { id: "cpp-code", type: "code", prompt: "C++ 代码题", choices: [], starter_code: "#include <iostream>", visible_tests: [], experience_points: 1 } } });

    await cpp.vm.$nextTick();
    expect(cpp.get("[data-code-editor]").attributes("data-language")).toBe("cpp");
    expect(cpp.get("textarea").attributes()).toMatchObject({ id: "cpp-editor", "aria-label": "C++ 代码编辑器" });
  });
});
