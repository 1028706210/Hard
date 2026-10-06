export type OfflineDraftKind = "progress" | "answer" | "note" | "code";
export interface OfflineDraftStorage { getItem(key: string): string | null; setItem(key: string, value: string): void; removeItem(key: string): void; }
export type CodeDraftState = "pending_runner" | "waiting_runner" | "pending_score" | "failed_runner";
export interface OfflineDraft { kind: OfflineDraftKind; url: string; method: "POST" | "PUT" | "PATCH"; body: Record<string, unknown>; idempotencyKey: string; state?: CodeDraftState; runnerJobId?: string; scoreIdempotencyKey?: string; failureReason?: string; }
export interface FlushResult { confirmed: string[]; pending: string[]; failed: string[]; }

const storageKey = "hard:offline-drafts";

function read(storage: OfflineDraftStorage): OfflineDraft[] {
  const value = storage.getItem(storageKey);
  if (!value) return [];
  try {
    const parsed: unknown = JSON.parse(value);
    if (!Array.isArray(parsed)) throw new Error("invalid drafts");
    return parsed.filter((draft): draft is OfflineDraft => {
      if (!draft || typeof draft !== "object") return false;
      const value = draft as Partial<OfflineDraft>;
      return ["progress", "answer", "note", "code"].includes(String(value.kind))
        && typeof value.url === "string" && typeof value.method === "string"
        && !!value.body && typeof value.body === "object" && typeof value.idempotencyKey === "string";
    });
  } catch {
    storage.removeItem(storageKey);
    return [];
  }
}

function write(storage: OfflineDraftStorage, drafts: readonly OfflineDraft[]) {
  if (drafts.length) storage.setItem(storageKey, JSON.stringify(drafts));
  else storage.removeItem(storageKey);
}

export function createOfflineDraftQueue(storage: OfflineDraftStorage = localStorage) {
  function items() { return read(storage); }
  function enqueue(draft: OfflineDraft) {
    const existing = items().filter((item) => item.idempotencyKey !== draft.idempotencyKey);
    write(storage, [...existing, draft]);
  }
  async function flush(fetchImpl: typeof fetch = fetch): Promise<FlushResult> {
    const confirmed: string[] = [];
    const failed: string[] = [];
    const pending: OfflineDraft[] = [];
    for (const draft of items()) {
      try {
        if (draft.kind === "code") {
          const state = draft.state ?? "pending_runner";
          if (state === "failed_runner") { pending.push(draft); failed.push(draft.idempotencyKey); continue; }
          if (state === "waiting_runner" && draft.runnerJobId) {
            const response = await fetchImpl(`/api/runners/jobs/${draft.runnerJobId}`);
            if (response.status === 404) { pending.push({ ...draft, state: "failed_runner", failureReason: "runner_not_found" }); failed.push(draft.idempotencyKey); continue; }
            if (!response.ok) { pending.push(draft); continue; }
            const job = await response.json() as Record<string, any>;
            const status = String(job.status);
            if (["succeeded", "failed"].includes(status)) {
              pending.push({ ...draft, state: "pending_score", url: "/api/assessment/attempts", method: "POST", body: { lesson_id: draft.body.lesson_id, exercise_id: draft.body.exercise_id, runner_job_id: draft.runnerJobId, hint_level: "none" } });
              continue;
            }
            if (["cancelled", "timed_out", "output_overflow", "rejected", "tool_missing"].includes(status)) {
              pending.push({ ...draft, state: "failed_runner", failureReason: status }); failed.push(draft.idempotencyKey); continue;
            }
            pending.push(draft); continue;
          }
          if (state === "pending_runner") {
            const response = await fetchImpl(draft.url, { method: draft.method, headers: { "content-type": "application/json", "Idempotency-Key": draft.idempotencyKey }, body: JSON.stringify(draft.body) });
            if (!response.ok) { pending.push(draft); continue; }
            const job = await response.json() as Record<string, unknown>;
            const jobId = typeof job.id === "string" ? job.id : "";
            if (!jobId) { pending.push(draft); continue; }
            pending.push({ ...draft, state: "waiting_runner", runnerJobId: jobId, scoreIdempotencyKey: draft.scoreIdempotencyKey ?? `${draft.idempotencyKey}:score` });
            continue;
          }
        }
        const response = await fetchImpl(draft.url, {
          method: draft.method,
          headers: { "content-type": "application/json", "Idempotency-Key": draft.state === "pending_score" ? (draft.scoreIdempotencyKey ?? `${draft.idempotencyKey}:score`) : draft.idempotencyKey },
          body: JSON.stringify(draft.body),
        });
        if (response.ok) { confirmed.push(draft.idempotencyKey); continue; }
      } catch { /* Leave transient network failures pending. */ }
      pending.push(draft);
    }
    write(storage, pending);
    return { confirmed, pending: pending.filter((draft) => draft.state !== "failed_runner").map((draft) => draft.idempotencyKey), failed };
  }
  function remove(idempotencyKey: string) { write(storage, items().filter((draft) => draft.idempotencyKey !== idempotencyKey)); }
  function retry(idempotencyKey: string, replacementKey: string) {
    write(storage, items().map((draft) => draft.idempotencyKey !== idempotencyKey ? draft : {
      ...draft, url: "/api/runners/submissions", method: "POST" as const, idempotencyKey: replacementKey, state: "pending_runner" as const,
      runnerJobId: undefined, scoreIdempotencyKey: undefined, failureReason: undefined,
    }));
  }
  return { items, enqueue, flush, remove, retry };
}

export function enqueueOfflineDraft(draft: OfflineDraft, storage: OfflineDraftStorage = localStorage) {
  createOfflineDraftQueue(storage).enqueue(draft);
}
