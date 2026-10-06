import { describe, expect, it, vi } from "vitest";

import { loadEditorDraft, saveEditorDraft } from "../../src/features/assessment/editor-drafts";
import { createAssessmentStore, type AssessmentLesson } from "../../src/features/assessment/assessment.store";


function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
}


function memoryStorage() {
  const values = new Map<string, string>();
  return { getItem: (key: string) => values.get(key) ?? null, setItem: (key: string, value: string) => values.set(key, value), removeItem: (key: string) => values.delete(key) };
}


const lesson: AssessmentLesson = {
  id: "python-foundations-hello-world",
  language: "python",
  exercises: [
    { id: "python-foundations-hello-world-k01", type: "knowledge", prompt: "选择 print", choices: [{ id: "a", text: "print" }], starter_code: null, visible_tests: [], experience_points: 10 },
    { id: "python-foundations-hello-world-c01", type: "code", prompt: "输出文本", choices: [], starter_code: "print('')", visible_tests: ["公开测试"], experience_points: 20 },
  ],
};


describe("assessment store", () => {
  it("submits a knowledge answer with hint penalty and a stable idempotency key", async () => {
    const fetchImpl = vi.fn().mockResolvedValueOnce(json(lesson)).mockResolvedValueOnce(json({ question_score: 85, total_score: 25.5, passed: false }));
    const store = createAssessmentStore(fetchImpl, memoryStorage(), () => "knowledge-key");

    await store.loadLesson(lesson.id);
    await store.submitKnowledge(lesson.exercises[0]!, "a", "light");

    expect(fetchImpl.mock.calls[1]?.[0]).toBe("/api/assessment/attempts");
    expect(fetchImpl.mock.calls[1]?.[1]).toMatchObject({ headers: { "Idempotency-Key": "knowledge-key" } });
    expect(JSON.parse(String(fetchImpl.mock.calls[1]?.[1]?.body))).toEqual({ lesson_id: lesson.id, exercise_id: lesson.exercises[0]!.id, answer: "a", hint_level: "light" });
    expect(store.state.assessment?.question_score).toBe(85);
  });

  it("uses only a server runner job when recording code score and exposes aggregate hidden failures", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(json(lesson))
      .mockResolvedValueOnce(json({ id: "job-1", status: "succeeded", result: { status: "succeeded", stdout: "Hello", diagnostics: [], duration_ms: 12, tests: { visible_passed: 1, visible_total: 1, hidden_passed: 0, hidden_total: 2 } } }))
      .mockResolvedValueOnce(json({ question_score: 33.33, total_score: 13.33, passed: false, review_status: "wrong_answer" }));
    const store = createAssessmentStore(fetchImpl, memoryStorage(), () => "code-key");

    await store.loadLesson(lesson.id);
    await store.runCode(lesson.exercises[1]!, "print('Hello')");

    const scoreRequest = JSON.parse(String(fetchImpl.mock.calls[2]?.[1]?.body));
    expect(scoreRequest).toEqual({ lesson_id: lesson.id, exercise_id: lesson.exercises[1]!.id, runner_job_id: "job-1", hint_level: "none" });
    expect(JSON.stringify(scoreRequest)).not.toContain("normalized_result");
    expect(store.state.run?.hidden_test_failures).toBe(2);
  });

  it("cancels a running job and restores the same code draft after refresh", async () => {
    const storage = memoryStorage();
    const fetchImpl = vi.fn().mockResolvedValueOnce(json({ id: "job-1", status: "cancelled", result: { status: "cancelled", error_code: "cancelled" } }));
    const store = createAssessmentStore(fetchImpl, storage, () => "draft-key");

    saveEditorDraft(storage, lesson.id, lesson.exercises[1]!.id, "print('draft')", "draft-key");
    await store.cancelRun("job-1");

    expect(loadEditorDraft(storage, lesson.id, lesson.exercises[1]!.id)).toEqual({ sourceCode: "print('draft')", idempotencyKey: "draft-key" });
    expect(store.state.run?.status).toBe("cancelled");
  });
});
