import { describe, expect, it, vi } from "vitest";

import { loadEditorDraft, saveEditorDraft } from "../../src/features/assessment/editor-drafts";
import { createAssessmentStore, type AssessmentLesson } from "../../src/features/assessment/assessment.store";
import { createOfflineDraftQueue } from "../../src/app/offline-drafts";


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
  it.each(["success", "failure"] as const)("keeps the latest answer feedback when an older same-question request ends in %s", async (outcome) => {
    let finishOld!: (response: Response) => void;
    let failOld!: (error: Error) => void;
    let key = 0;
    const storage = memoryStorage();
    const fetchImpl = vi.fn((input: RequestInfo | URL, options?: RequestInit) => {
      if (String(input).startsWith("/api/content/")) return Promise.resolve(json(lesson));
      if (input === "/api/assessment/attempts") {
        const payload = JSON.parse(String(options?.body));
        if (payload.answer === "old") return new Promise<Response>((resolve, reject) => { finishOld = resolve; failOld = reject; });
        return Promise.resolve(json({ question_score: 85, total_score: 25.5, passed: true }));
      }
      return Promise.resolve(json({}));
    });
    const store = createAssessmentStore(fetchImpl, storage, () => `answer-${++key}`);
    await store.loadLesson(lesson.id);
    const oldPending = store.submitKnowledge(lesson.exercises[0]!, "old", "none");
    await store.submitKnowledge(lesson.exercises[0]!, "latest", "light");
    if (outcome === "success") finishOld(json({ question_score: 0, total_score: 0, passed: false }));
    else failOld(new Error("old request offline"));
    await oldPending;

    expect(store.state.assessment?.question_score).toBe(85);
    expect(store.state.error).toBe("");
    const drafts = createOfflineDraftQueue(storage).items();
    if (outcome === "failure") {
      expect(drafts).toEqual([expect.objectContaining({ idempotencyKey: "answer-1", body: { lesson_id: lesson.id, exercise_id: lesson.exercises[0]!.id, answer: "old", hint_level: "none" } })]);
    } else expect(drafts).toEqual([]);
  });

  it("keeps the newest answer failure when an older same-question request succeeds later", async () => {
    let finishOld!: (response: Response) => void;
    const storage = memoryStorage();
    let key = 0;
    const fetchImpl = vi.fn((input: RequestInfo | URL, options?: RequestInit) => {
      if (String(input).startsWith("/api/content/")) return Promise.resolve(json(lesson));
      if (input === "/api/assessment/attempts") {
        if (JSON.parse(String(options?.body)).answer === "old") return new Promise<Response>(resolve => { finishOld = resolve; });
        return Promise.reject(new Error("latest request offline"));
      }
      return Promise.resolve(json({}));
    });
    const store = createAssessmentStore(fetchImpl, storage, () => `answer-${++key}`);
    await store.loadLesson(lesson.id);
    const oldPending = store.submitKnowledge(lesson.exercises[0]!, "old", "none");
    await store.submitKnowledge(lesson.exercises[0]!, "latest", "strong");
    finishOld(json({ question_score: 100, total_score: 50, passed: true }));
    await oldPending;

    expect(store.state.assessment).toBeNull();
    expect(store.state.error).toContain("离线草稿");
    expect(createOfflineDraftQueue(storage).items()).toEqual([expect.objectContaining({ idempotencyKey: "answer-2", body: { lesson_id: lesson.id, exercise_id: lesson.exercises[0]!.id, answer: "latest", hint_level: "strong" } })]);
  });

  it("does not expose an old lesson's late successful answer on the same exercise id after navigation", async () => {
    let finishOld!: (response: Response) => void;
    const anotherLesson = { ...lesson, id: "another-lesson" };
    const fetchImpl = vi.fn((input: RequestInfo | URL, options?: RequestInit) => {
      if (input === `/api/content/lessons/${lesson.id}`) return Promise.resolve(json(lesson));
      if (input === `/api/content/lessons/${anotherLesson.id}`) return Promise.resolve(json(anotherLesson));
      if (input === "/api/assessment/attempts") {
        if (JSON.parse(String(options?.body)).lesson_id === lesson.id) return new Promise<Response>(resolve => { finishOld = resolve; });
        return Promise.resolve(json({ question_score: 60, total_score: 20, passed: false }));
      }
      return Promise.resolve(json({}));
    });
    const store = createAssessmentStore(fetchImpl, memoryStorage());
    await store.loadLesson(lesson.id);
    const oldPending = store.submitKnowledge(lesson.exercises[0]!, "a", "none");
    await store.loadLesson(anotherLesson.id);
    await store.submitKnowledge(anotherLesson.exercises[0]!, "a", "strong");
    finishOld(json({ question_score: 100, total_score: 50, passed: true }));
    await oldPending;
    expect(store.state.lesson?.id).toBe(anotherLesson.id);
    expect(store.state.assessment?.question_score).toBe(60);
    expect(store.state.error).toBe("");
  });

  it("keeps a confirmed cancellation when an older poll finishes later", async () => {
    vi.useFakeTimers();
    try {
      let finishPoll!: (response: Response) => void;
      const fetchImpl = vi.fn((input: RequestInfo | URL, options?: RequestInit) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
        if (url.startsWith("/api/content/")) return Promise.resolve(json(lesson));
        if (url === "/api/runners/submissions") return Promise.resolve(json({ id: "cancel-job", status: "running" }));
        if (options?.method === "DELETE") return Promise.resolve(json({ id: "cancel-job", status: "cancelled" }));
        return new Promise<Response>(resolve => { finishPoll = resolve; });
      });
      const storage = memoryStorage();
      const store = createAssessmentStore(fetchImpl, storage, () => "cancel-key");
      await store.loadLesson(lesson.id);
      const pending = store.runCode(lesson.exercises[1]!, "print('keep')");
      await vi.advanceTimersByTimeAsync(400);
      await store.cancelRun("cancel-job");
      finishPoll(json({ id: "cancel-job", status: "succeeded", result: { diagnostics: [] } }));
      await pending;
      expect(store.state.run?.status).toBe("cancelled");
      expect(store.state.runState).toBe("cancelled");
      expect(store.state.assessment).toBeNull();
      expect(fetchImpl.mock.calls.some(([url]) => url === "/api/assessment/attempts")).toBe(false);
      expect(loadEditorDraft(storage, lesson.id, lesson.exercises[1]!.id)?.sourceCode).toBe("print('keep')");
    } finally { vi.useRealTimers(); }
  });

  it("scores a late completed run for its original lesson and preserves a newer code draft", async () => {
    let finishRun!: (response: Response) => void;
    const storage = memoryStorage();
    const nextLesson = { ...lesson, id: "new-lesson" };
    const fetchImpl = vi.fn((input: RequestInfo | URL, _options?: RequestInit) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
      if (url === `/api/content/lessons/${lesson.id}`) return Promise.resolve(json(lesson));
      if (url === `/api/content/lessons/${nextLesson.id}`) return Promise.resolve(json(nextLesson));
      if (url === "/api/runners/submissions") return new Promise<Response>(resolve => { finishRun = resolve; });
      return Promise.resolve(json({ question_score: 100, total_score: 50, passed: true }));
    });
    const store = createAssessmentStore(fetchImpl, storage, () => "original-key");
    const code = lesson.exercises[1]!;
    await store.loadLesson(lesson.id);
    const pending = store.runCode(code, "print('original')");
    saveEditorDraft(storage, lesson.id, code.id, "print('new draft')", "new-key");
    await store.loadLesson(nextLesson.id);
    finishRun(json({ id: "old-job", status: "succeeded", result: { diagnostics: [] } }));
    await pending;
    expect(store.state.assessment).toBeNull();
    expect(store.state.run).toBeNull();
    const scoring = fetchImpl.mock.calls.find(([url]) => url === "/api/assessment/attempts");
    expect(JSON.parse(String(scoring?.[1]?.body))).toMatchObject({ lesson_id: lesson.id, exercise_id: code.id, runner_job_id: "old-job" });
    expect(loadEditorDraft(storage, lesson.id, code.id)).toEqual({ sourceCode: "print('new draft')", idempotencyKey: "new-key" });
  });

  it("keeps a late answer response on its exercise without replacing the selected exercise score", async () => {
    let finishFirst!: (response: Response) => void;
    const second = { ...lesson.exercises[0]!, id: "second-knowledge" };
    const withTwoQuestions = { ...lesson, exercises: [lesson.exercises[0]!, second] };
    const fetchImpl = vi.fn((input: RequestInfo | URL, options?: RequestInit) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
      if (url.startsWith("/api/content/")) return Promise.resolve(json(withTwoQuestions));
      if (url === "/api/assessment/attempts") {
        const payload = JSON.parse(String(options?.body));
        if (payload.exercise_id === second.id) return Promise.resolve(json({ question_score: 60, total_score: 20, passed: false }));
        return new Promise<Response>(resolve => { finishFirst = resolve; });
      }
      return Promise.resolve(json({}));
    });
    const store = createAssessmentStore(fetchImpl, memoryStorage());
    await store.loadLesson(lesson.id);
    const firstPending = store.submitKnowledge(lesson.exercises[0]!, "a", "none");
    store.selectExercise(second.id);
    expect(store.state.assessment).toBeNull();
    await store.submitKnowledge(second, "a", "strong");
    finishFirst(json({ question_score: 100, total_score: 50, passed: true }));
    await firstPending;
    expect(store.state.assessment?.question_score).toBe(60);
    store.selectExercise(lesson.exercises[0]!.id);
    expect(store.state.assessment?.question_score).toBe(100);
  });

  it("keeps a late runner response, score, and draft cleanup on the originating exercise", async () => {
    let finishRun!: (response: Response) => void;
    const storage = memoryStorage();
    const code = lesson.exercises[1]!;
    const fetchImpl = vi.fn((input: RequestInfo | URL, options?: RequestInit) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
      if (url.startsWith("/api/content/")) return Promise.resolve(json(lesson));
      if (url === "/api/runners/submissions") return new Promise<Response>(resolve => { finishRun = resolve; });
      if (url === "/api/assessment/attempts") return Promise.resolve(json({ question_score: 100, total_score: 50, passed: true }));
      return Promise.resolve(json({}));
    });
    const store = createAssessmentStore(fetchImpl, storage, () => "owned-key");
    await store.loadLesson(lesson.id);
    store.selectExercise(code.id);
    const pending = store.runCode(code, "print('draft')");
    expect(store.state.runState).toBe("running");
    store.selectExercise(lesson.exercises[0]!.id);
    expect(store.state.run).toBeNull();
    expect(store.state.runState).toBe("idle");
    finishRun(json({ id: "owned-job", status: "succeeded", result: { diagnostics: [], tests: { visible_passed: 1, visible_total: 1 } } }));
    await pending;
    expect(store.state.run).toBeNull();
    expect(store.state.assessment).toBeNull();
    store.selectExercise(code.id);
    expect(store.state.run?.status).toBe("succeeded");
    expect(store.state.assessment?.question_score).toBe(100);
    const scoring = fetchImpl.mock.calls.find(([url, options]) => url === "/api/assessment/attempts" && String(options?.body).includes("owned-job"));
    expect(JSON.parse(String(scoring?.[1]?.body))).toMatchObject({ lesson_id: lesson.id, exercise_id: code.id, runner_job_id: "owned-job" });
    expect(scoring?.[1]?.headers).toMatchObject({ "Idempotency-Key": "owned-key" });
    expect(loadEditorDraft(storage, lesson.id, code.id)).toBeNull();
  });

  it("does not expose an old lesson's late failure in a newly loaded lesson", async () => {
    let failOld!: (error: Error) => void;
    const anotherLesson = { ...lesson, id: "another-lesson" };
    const fetchImpl = vi.fn((input: RequestInfo | URL, _options?: RequestInit) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
      if (url === `/api/content/lessons/${lesson.id}`) return Promise.resolve(json(lesson));
      if (url === `/api/content/lessons/${anotherLesson.id}`) return Promise.resolve(json(anotherLesson));
      return new Promise<Response>((_, reject) => { failOld = reject; });
    });
    const store = createAssessmentStore(fetchImpl, memoryStorage());
    await store.loadLesson(lesson.id);
    const pending = store.submitKnowledge(lesson.exercises[0]!, "a", "none");
    await store.loadLesson(anotherLesson.id);
    failOld(new Error("old request offline"));
    await pending;
    expect(store.state.lesson?.id).toBe(anotherLesson.id);
    expect(store.state.error).toBe("");
    expect(store.state.assessment).toBeNull();
  });

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

  it("uses the public runner result only and clears a draft after scoring succeeds", async () => {
    const storage = memoryStorage();
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(json(lesson))
      .mockResolvedValueOnce(json({ id: "job-1", status: "succeeded", result: { status: "succeeded", diagnostics: [], tests: { visible_passed: 1, visible_total: 1 } } }))
      .mockResolvedValueOnce(json({ question_score: 33.33, total_score: 13.33, passed: false, review_status: "wrong_answer" }));
    const store = createAssessmentStore(fetchImpl, storage, () => "code-key");

    await store.loadLesson(lesson.id);
    await store.runCode(lesson.exercises[1]!, "print('Hello')");

    const scoreRequest = JSON.parse(String(fetchImpl.mock.calls[2]?.[1]?.body));
    expect(scoreRequest).toEqual({ lesson_id: lesson.id, exercise_id: lesson.exercises[1]!.id, runner_job_id: "job-1", hint_level: "none" });
    expect(JSON.stringify(scoreRequest)).not.toContain("normalized_result");
    expect(store.state.run).toMatchObject({ status: "succeeded", tests: { visible_passed: 1, visible_total: 1 } });
    expect(loadEditorDraft(storage, lesson.id, lesson.exercises[1]!.id)).toBeNull();
  });

  it("turns a runner submission network failure into a terminal error while retaining the draft", async () => {
    const storage = memoryStorage();
    const fetchImpl = vi.fn().mockResolvedValueOnce(json(lesson)).mockRejectedValueOnce(new Error("network down"));
    const store = createAssessmentStore(fetchImpl, storage, () => "offline-key");

    await store.loadLesson(lesson.id);
    await store.runCode(lesson.exercises[1]!, "print('draft')");

    expect(store.state.runState).toBe("error");
    expect(store.state.run?.status).toBe("interrupted");
    expect(store.state.runningJobId).toBe("");
    expect(store.state.error).toContain("草稿已保留");
    expect(loadEditorDraft(storage, lesson.id, lesson.exercises[1]!.id)).toEqual({ sourceCode: "print('draft')", idempotencyKey: "offline-key" });
  });

  it("ends polling on a network interruption instead of leaving the runner active", async () => {
    vi.useFakeTimers();
    const storage = memoryStorage();
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(json(lesson))
      .mockResolvedValueOnce(json({ id: "job-1", status: "running", result: null }))
      .mockRejectedValueOnce(new Error("polling interrupted"));
    const store = createAssessmentStore(fetchImpl, storage, () => "poll-key");

    await store.loadLesson(lesson.id);
    const pending = store.runCode(lesson.exercises[1]!, "print('draft')");
    await vi.advanceTimersByTimeAsync(400);
    await pending;

    expect(store.state.runState).toBe("error");
    expect(store.state.run?.status).toBe("interrupted");
    expect(store.state.runningJobId).toBe("");
    expect(loadEditorDraft(storage, lesson.id, lesson.exercises[1]!.id)).not.toBeNull();
    vi.useRealTimers();
  });

  it("ends on a total runner timeout while retaining the draft", async () => {
    vi.useFakeTimers();
    const storage = memoryStorage();
    const fetchImpl = vi.fn()
      .mockResolvedValueOnce(json(lesson))
      .mockResolvedValueOnce(json({ id: "job-1", status: "running", result: null }))
      .mockImplementation(() => Promise.resolve(json({ id: "job-1", status: "running", result: null })));
    const store = createAssessmentStore(fetchImpl, storage, () => "timeout-key");

    await store.loadLesson(lesson.id);
    const pending = store.runCode(lesson.exercises[1]!, "print('draft')");
    await vi.advanceTimersByTimeAsync(30_400);
    await pending;

    expect(store.state.runState).toBe("timed_out");
    expect(store.state.run?.status).toBe("timed_out");
    expect(store.state.runningJobId).toBe("");
    expect(loadEditorDraft(storage, lesson.id, lesson.exercises[1]!.id)).not.toBeNull();
    vi.useRealTimers();
  });

  it("ends scoring failure and cancellation failure with an actionable retained-draft error", async () => {
    const storage = memoryStorage();
    const scoringFailure = vi.fn()
      .mockResolvedValueOnce(json(lesson))
      .mockResolvedValueOnce(json({ id: "job-1", status: "succeeded", result: { status: "succeeded", diagnostics: [] } }))
      .mockRejectedValueOnce(new Error("score offline"));
    const store = createAssessmentStore(scoringFailure, storage, () => "score-key");

    await store.loadLesson(lesson.id);
    await store.runCode(lesson.exercises[1]!, "print('draft')");
    expect(store.state.runState).toBe("error");
    expect(store.state.error).toContain("评分尚未保存");
    expect(loadEditorDraft(storage, lesson.id, lesson.exercises[1]!.id)).not.toBeNull();

    const cancelFailure = createAssessmentStore(vi.fn().mockRejectedValue(new Error("cancel offline")), storage);
    await cancelFailure.cancelRun("job-1");
    expect(cancelFailure.state.runState).toBe("error");
    expect(cancelFailure.state.runningJobId).toBe("");
    expect(cancelFailure.state.error).toContain("无法取消运行");
  });

  it("reports lesson loading failure as a retryable error state", async () => {
    const store = createAssessmentStore(vi.fn().mockRejectedValue(new Error("offline")), memoryStorage());

    await store.loadLesson(lesson.id);

    expect(store.state.loadState).toBe("error");
    expect(store.state.lesson).toBeNull();
    expect(store.state.error).toContain("重新读取");
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
