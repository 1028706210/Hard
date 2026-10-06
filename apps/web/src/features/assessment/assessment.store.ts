import { reactive, readonly } from "vue";

import { requestJson } from "../../api/client";
import { enqueueOfflineDraft } from "../../app/offline-drafts";
import { loadEditorDraft, saveEditorDraft } from "./editor-drafts";
import { refreshMapSnapshot } from "../map/map.store";

export interface Exercise {
  readonly id: string;
  readonly type: "knowledge" | "code" | "challenge" | "scenario";
  readonly prompt: string;
  readonly choices: ReadonlyArray<{ readonly id: string; readonly text: string }>;
  readonly starter_code: string | null;
  readonly visible_tests: readonly string[];
  readonly experience_points: number;
}
export interface AssessmentLesson { readonly id: string; readonly language: string; readonly exercises: readonly Exercise[]; }
export interface RunView {
  readonly status: string;
  readonly stdout: string;
  readonly diagnostics: readonly string[];
  readonly duration_ms: number;
  readonly hidden_test_failures: number;
  readonly error_code?: string | null;
}
interface StorageLike { getItem(key: string): string | null; setItem(key: string, value: string): void; removeItem(key: string): void; }
const terminalStatuses = new Set(["succeeded", "failed", "cancelled", "timed_out", "output_overflow", "rejected", "tool_missing"]);

function generatedKey() { return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`; }
function runView(payload: any): RunView {
  const result = payload.result ?? payload;
  const tests = result.tests ?? {};
  return {
    status: String(payload.status ?? result.status ?? "failed"),
    stdout: String(result.stdout ?? ""),
    diagnostics: Array.isArray(result.diagnostics) ? result.diagnostics.map(String) : [],
    duration_ms: Number(result.duration_ms ?? 0),
    hidden_test_failures: Math.max(0, Number(tests.hidden_total ?? 0) - Number(tests.hidden_passed ?? 0)),
    error_code: result.error_code == null ? null : String(result.error_code),
  };
}

export function createAssessmentStore(
  fetchImpl: typeof fetch = fetch,
  storage: StorageLike = localStorage,
  createKey: () => string = generatedKey,
) {
  const state = reactive({ lesson: null as AssessmentLesson | null, run: null as RunView | null, assessment: null as Record<string, any> | null, error: "", runningJobId: "" });

  async function loadLesson(lessonId: string) {
    state.lesson = await requestJson<AssessmentLesson>(`/api/content/lessons/${lessonId}`, undefined, fetchImpl);
    state.run = null;
    state.assessment = null;
  }

  async function submitKnowledge(exercise: Exercise, answer: string, hintLevel: string) {
    if (!state.lesson) throw new Error("lesson_not_loaded");
    const idempotencyKey = createKey();
    const payload = { lesson_id: state.lesson.id, exercise_id: exercise.id, answer, hint_level: hintLevel };
    try {
    const response = await requestJson<Record<string, any>>("/api/assessment/attempts", {
      method: "POST",
      headers: { "content-type": "application/json", "Idempotency-Key": idempotencyKey },
      body: JSON.stringify(payload),
    }, fetchImpl);
    state.assessment = response;
    void refreshMapSnapshot(fetchImpl);
    return response;
    } catch (error) { enqueueOfflineDraft({ kind: "answer", url: "/api/assessment/attempts", method: "POST", body: payload, idempotencyKey }, storage); throw error; }
  }

  async function runCode(exercise: Exercise, sourceCode: string) {
    if (!state.lesson) throw new Error("lesson_not_loaded");
    const existing = loadEditorDraft(storage, state.lesson.id, exercise.id);
    const idempotencyKey = existing?.sourceCode === sourceCode ? existing.idempotencyKey : createKey();
    saveEditorDraft(storage, state.lesson.id, exercise.id, sourceCode, idempotencyKey);
    const runnerPayload = { lesson_id: state.lesson.id, exercise_id: exercise.id, source_code: sourceCode, stdin: "" };
    let job: Record<string, any>;
    try { job = await requestJson<Record<string, any>>("/api/runners/submissions", {
      method: "POST",
      headers: { "content-type": "application/json", "Idempotency-Key": idempotencyKey },
      body: JSON.stringify(runnerPayload),
    }, fetchImpl); } catch (error) { enqueueOfflineDraft({ kind: "code", state: "pending_runner", url: "/api/runners/submissions", method: "POST", body: runnerPayload, idempotencyKey, scoreIdempotencyKey: createKey() }, storage); throw error; }
    state.runningJobId = String(job.id);
    state.run = runView(job);
    return await resolveRun(exercise, job, idempotencyKey);
  }

  async function resolveRun(exercise: Exercise, job: Record<string, any>, idempotencyKey: string): Promise<RunView> {
    if (!state.lesson) throw new Error("lesson_not_loaded");
    let current = job;
    const deadline = Date.now() + 30_000;
    while (!terminalStatuses.has(String(current.status)) && Date.now() < deadline) {
      await new Promise((resolve) => window.setTimeout(resolve, 400));
      current = await requestJson<Record<string, any>>(`/api/runners/jobs/${state.runningJobId}`, undefined, fetchImpl);
    }
    const result = runView(current);
    state.run = result;
    if (result.status === "succeeded" || result.status === "failed") {
      state.assessment = await requestJson<Record<string, any>>("/api/assessment/attempts", {
        method: "POST",
        headers: { "content-type": "application/json", "Idempotency-Key": idempotencyKey },
        body: JSON.stringify({ lesson_id: state.lesson.id, exercise_id: exercise.id, runner_job_id: state.runningJobId, hint_level: "none" }),
      }, fetchImpl);
      void refreshMapSnapshot(fetchImpl);
    }
    return result;
  }

  async function cancelRun(jobId: string) {
    const cancelled = await requestJson<Record<string, any>>(`/api/runners/jobs/${jobId}`, { method: "DELETE" }, fetchImpl);
    state.run = runView(cancelled);
    state.runningJobId = "";
    return state.run;
  }

  return { state: readonly(state), loadLesson, submitKnowledge, runCode, cancelRun };
}

export const assessmentStore = createAssessmentStore();
