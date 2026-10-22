import { computed, reactive, readonly, ref } from "vue";

import { requestJson, type AttemptResponse, type LessonResponse, type RunnerJobCancelResponse, type RunnerJobStatusResponse, type RunnerSubmissionResponse } from "../../api/client";
import { enqueueOfflineDraft } from "../../app/offline-drafts";
import { clearEditorDraft, loadEditorDraft, saveEditorDraft, type EditorDraftStorage } from "./editor-drafts";
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
  readonly diagnostics: readonly string[];
  readonly tests: { readonly visible_passed: number; readonly visible_total: number } | null;
}
export type AssessmentLoadState = "idle" | "loading" | "ready" | "error";
export type RunState = "idle" | "running" | "completed" | "cancelled" | "timed_out" | "error";

type ApiObject = Record<string, unknown>;
const terminalStatuses = new Set(["succeeded", "failed", "cancelled", "timed_out", "output_overflow", "rejected", "tool_missing"]);

function generatedKey() { return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`; }
function asObject(value: unknown): ApiObject { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as ApiObject : {}; }
function asNumber(value: unknown) { return typeof value === "number" && Number.isFinite(value) ? value : 0; }
function runView(payload: unknown): RunView {
  const job = asObject(payload);
  const result = asObject(job.result);
  const source = Object.keys(result).length ? result : job;
  const tests = asObject(source.tests);
  return {
    status: String(job.status ?? source.status ?? "failed"),
    diagnostics: Array.isArray(source.diagnostics) ? source.diagnostics.map(String) : [],
    tests: Object.keys(tests).length ? { visible_passed: asNumber(tests.visible_passed), visible_total: asNumber(tests.visible_total) } : null,
  };
}

export function createAssessmentStore(fetchImpl: typeof fetch = fetch, storage: EditorDraftStorage = localStorage, createKey: () => string = generatedKey) {
  interface ExerciseFeedback {
    run: RunView | null;
    assessment: AttemptResponse | null;
    error: string;
    runState: RunState;
    runningJobId: string;
    runRevision: number;
    knowledgeRevision: number;
  }
  const feedbackByExercise = reactive(new Map<string, ExerciseFeedback>());
  const selectedExerciseId = ref("");
  const loadError = ref("");
  let loadRevision = 0;
  function feedbackFor(exerciseId: string): ExerciseFeedback {
    if (!feedbackByExercise.has(exerciseId)) feedbackByExercise.set(exerciseId, { run: null, assessment: null, error: "", runState: "idle", runningJobId: "", runRevision: 0, knowledgeRevision: 0 });
    return feedbackByExercise.get(exerciseId)!;
  }
  const currentFeedback = computed(() => feedbackFor(selectedExerciseId.value));
  const state = reactive({
    lesson: null as AssessmentLesson | null,
    loadState: "idle" as AssessmentLoadState,
    run: computed(() => currentFeedback.value.run),
    assessment: computed(() => currentFeedback.value.assessment),
    error: computed(() => loadError.value || currentFeedback.value.error),
    runState: computed(() => currentFeedback.value.runState),
    runningJobId: computed(() => currentFeedback.value.runningJobId),
  });

  function selectExercise(exerciseId: string) { selectedExerciseId.value = exerciseId; }

  function setRunError(feedback: ExerciseFeedback, message: string, status = "interrupted") {
    feedback.run = { status, diagnostics: [message], tests: null };
    feedback.runState = "error";
    feedback.runningJobId = "";
    feedback.error = message;
    return feedback.run;
  }

  async function loadLesson(lessonId: string) {
    const revision = ++loadRevision;
    state.loadState = "loading";
    loadError.value = "";
    state.lesson = null;
    feedbackByExercise.clear();
    selectedExerciseId.value = "";
    try {
      const lesson = await requestJson<LessonResponse>(`/api/content/lessons/${lessonId}`, undefined, fetchImpl) as unknown as AssessmentLesson;
      if (revision !== loadRevision) return null;
      state.lesson = lesson;
      selectExercise(lesson.exercises[0]?.id ?? "");
      state.loadState = "ready";
      return state.lesson;
    } catch {
      if (revision !== loadRevision) return null;
      state.loadState = "error";
      loadError.value = "无法读取练习。请检查连接后重新读取。";
      return null;
    }
  }

  async function submitKnowledge(exercise: Exercise, answer: string, hintLevel: string) {
    if (!state.lesson) return null;
    selectExercise(exercise.id);
    const feedback = feedbackFor(exercise.id);
    const revision = ++feedback.knowledgeRevision;
    const idempotencyKey = createKey();
    const payload = { lesson_id: state.lesson.id, exercise_id: exercise.id, answer, hint_level: hintLevel };
    feedback.error = "";
    try {
      const response = await requestJson<AttemptResponse>("/api/assessment/attempts", { method: "POST", headers: { "content-type": "application/json", "Idempotency-Key": idempotencyKey }, body: JSON.stringify(payload) }, fetchImpl);
      if (revision !== feedback.knowledgeRevision) return null;
      feedback.assessment = response;
      void refreshMapSnapshot(fetchImpl);
      return response;
    } catch {
      enqueueOfflineDraft({ kind: "answer", url: "/api/assessment/attempts", method: "POST", body: payload, idempotencyKey }, storage);
      if (revision !== feedback.knowledgeRevision) return null;
      feedback.error = "答案尚未保存，已保留为离线草稿。请恢复连接后重试。";
      return null;
    }
  }

  async function runCode(exercise: Exercise, sourceCode: string) {
    if (!state.lesson) return null;
    selectExercise(exercise.id);
    const lessonId = state.lesson.id;
    const feedback = feedbackFor(exercise.id);
    const revision = ++feedback.runRevision;
    const existing = loadEditorDraft(storage, lessonId, exercise.id);
    const idempotencyKey = existing?.sourceCode === sourceCode ? existing.idempotencyKey : createKey();
    saveEditorDraft(storage, lessonId, exercise.id, sourceCode, idempotencyKey);
    const runnerPayload = { lesson_id: lessonId, exercise_id: exercise.id, source_code: sourceCode, stdin: "" };
    feedback.error = "";
    feedback.assessment = null;
    feedback.runningJobId = "";
    feedback.runState = "running";
    feedback.run = { status: "queued", diagnostics: [], tests: null };
    let job: RunnerSubmissionResponse;
    try {
      job = await requestJson<RunnerSubmissionResponse>("/api/runners/submissions", { method: "POST", headers: { "content-type": "application/json", "Idempotency-Key": idempotencyKey }, body: JSON.stringify(runnerPayload) }, fetchImpl);
    } catch {
      enqueueOfflineDraft({ kind: "code", state: "pending_runner", url: "/api/runners/submissions", method: "POST", body: runnerPayload, idempotencyKey, scoreIdempotencyKey: createKey() }, storage);
      if (revision !== feedback.runRevision) return null;
      return setRunError(feedback, "无法提交运行任务，草稿已保留。请检查连接后重试。");
    }
    if (revision !== feedback.runRevision) return null;
    const jobData = asObject(job);
    feedback.runningJobId = typeof jobData.id === "string" ? jobData.id : "";
    if (!feedback.runningJobId) return setRunError(feedback, "运行服务未返回任务编号，草稿已保留。请重试。");
    feedback.run = runView(job);
    return resolveRun(lessonId, exercise, job, idempotencyKey, feedback, revision);
  }

  async function resolveRun(lessonId: string, exercise: Exercise, job: RunnerSubmissionResponse, idempotencyKey: string, feedback: ExerciseFeedback, revision: number): Promise<RunView | null> {
    let current: RunnerJobStatusResponse | RunnerSubmissionResponse = job;
    const jobId = feedback.runningJobId;
    const deadline = Date.now() + 30_000;
    try {
      while (!terminalStatuses.has(runView(current).status) && Date.now() < deadline) {
        await new Promise((resolve) => window.setTimeout(resolve, 400));
        if (revision !== feedback.runRevision) return null;
        current = await requestJson<RunnerJobStatusResponse>(`/api/runners/jobs/${jobId}`, undefined, fetchImpl);
        if (revision !== feedback.runRevision) return null;
      }
    } catch {
      if (revision !== feedback.runRevision) return null;
      return setRunError(feedback, "运行状态同步中断，草稿已保留。请恢复连接后重试。");
    }
    if (!terminalStatuses.has(runView(current).status)) {
      feedback.run = { status: "timed_out", diagnostics: ["运行等待超时，草稿已保留。请稍后重试。"], tests: null };
      feedback.runState = "timed_out";
      feedback.runningJobId = "";
      feedback.error = "运行等待超时，草稿已保留。请稍后重试。";
      return feedback.run;
    }
    const result = runView(current);
    feedback.run = result;
    feedback.runningJobId = "";
    if (result.status === "cancelled") {
      feedback.runState = "cancelled";
      return result;
    }
    if (result.status !== "succeeded" && result.status !== "failed") {
      feedback.runState = result.status === "timed_out" ? "timed_out" : "error";
      feedback.error = "运行未完成，草稿已保留。请根据公开反馈调整后重试。";
      return result;
    }
    try {
      const assessment = await requestJson<AttemptResponse>("/api/assessment/attempts", { method: "POST", headers: { "content-type": "application/json", "Idempotency-Key": idempotencyKey }, body: JSON.stringify({ lesson_id: lessonId, exercise_id: exercise.id, runner_job_id: jobId, hint_level: "none" }) }, fetchImpl);
      if (revision !== feedback.runRevision) return null;
      feedback.assessment = assessment;
      const draft = loadEditorDraft(storage, lessonId, exercise.id);
      if (draft?.idempotencyKey === idempotencyKey) clearEditorDraft(storage, lessonId, exercise.id);
      feedback.runState = "completed";
      void refreshMapSnapshot(fetchImpl);
    } catch {
      if (revision !== feedback.runRevision) return null;
      feedback.runState = "error";
      feedback.error = "运行已结束，但评分尚未保存，草稿已保留。请恢复连接后重试。";
    }
    return result;
  }

  async function cancelRun(jobId: string) {
    const feedback = [...feedbackByExercise.values()].find(item => item.runningJobId === jobId) ?? feedbackFor(selectedExerciseId.value);
    const revision = ++feedback.runRevision;
    feedback.error = "";
    try {
      const cancelled = await requestJson<RunnerJobCancelResponse>(`/api/runners/jobs/${jobId}`, { method: "DELETE" }, fetchImpl);
      if (revision !== feedback.runRevision) return null;
      feedback.run = runView(cancelled);
      feedback.runningJobId = "";
      if (feedback.run.status === "cancelled") {
        feedback.runState = "cancelled";
        return feedback.run;
      }
      feedback.runState = "error";
      feedback.error = "取消请求尚未确认，草稿已保留。请检查连接后重试。";
      return feedback.run;
    } catch {
      if (revision !== feedback.runRevision) return null;
      return setRunError(feedback, "无法取消运行，草稿已保留。请检查连接后重试。");
    }
  }

  return { state: readonly(state), loadLesson, selectExercise, submitKnowledge, runCode, cancelRun };
}

export const assessmentStore = createAssessmentStore();
