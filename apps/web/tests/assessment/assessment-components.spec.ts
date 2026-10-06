import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import KnowledgeQuestion from "../../src/features/assessment/KnowledgeQuestion.vue";
import RunResult from "../../src/features/assessment/RunResult.vue";


describe("assessment components", () => {
  it("shows hint impact before a knowledge answer and never renders runner text as HTML", async () => {
    const question = mount(KnowledgeQuestion, { props: { exercise: { id: "k01", type: "knowledge", prompt: "题目", choices: [{ id: "a", text: "答案" }] } } });
    await question.findAll("button")[1]!.trigger("click");
    expect(question.text()).toContain("轻提示后本题最高 85% 分");

    const result = mount(RunResult, { props: { result: { status: "failed", stdout: "<script>output</script>", diagnostics: ["运行时错误"], duration_ms: 4, hidden_test_failures: 2 } } });
    expect(result.html()).toContain("&lt;script&gt;output&lt;/script&gt;");
    expect(result.html()).not.toContain("<script>output</script>");
    expect(result.text()).toContain("隐藏测试失败：2");
  });
});
