import { describe, expect, it, vi } from "vitest";

import { createOfflineDraftQueue, type OfflineDraftStorage } from "../src/app/offline-drafts";


function storage(): OfflineDraftStorage {
  const values = new Map<string, string>();
  return { getItem: (key) => values.get(key) ?? null, setItem: (key, value) => values.set(key, value), removeItem: (key) => values.delete(key) };
}

describe("offline drafts", () => {
  it("survives refreshes and replays only unconfirmed position, answer, note, and code requests with original keys", async () => {
    const local = storage();
    const first = createOfflineDraftQueue(local);
    first.enqueue({ kind: "progress", url: "/api/progress/lessons/l1", method: "PATCH", body: { position: 8, time_spent_seconds: 10 }, idempotencyKey: "progress-1" });
    first.enqueue({ kind: "answer", url: "/api/assessment/attempts", method: "POST", body: { answer: "a" }, idempotencyKey: "answer-1" });
    first.enqueue({ kind: "note", url: "/api/progress/notes/l1", method: "PUT", body: { body: "笔记" }, idempotencyKey: "note-1" });
    first.enqueue({ kind: "code", url: "/api/runners/submissions", method: "POST", body: { source_code: "print(1)" }, idempotencyKey: "code-1" });
    first.enqueue({ kind: "code", url: "/api/runners/submissions", method: "POST", body: { source_code: "print(1)" }, idempotencyKey: "code-1" });

    const reloaded = createOfflineDraftQueue(local);
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const key = (init?.headers as Record<string, string>)["Idempotency-Key"];
      if (key === "answer-1") return new Response("unavailable", { status: 503 });
      if (String(input) === "/api/runners/submissions") return new Response('{"id":"job-1"}', { status: 200, headers: { "content-type": "application/json" } });
      return new Response("{}", { status: 200, headers: { "content-type": "application/json" } });
    });
    const result = await reloaded.flush(fetchMock);

    expect(fetchMock).toHaveBeenCalledTimes(4);
    expect(result.confirmed).toEqual(["progress-1", "note-1"]);
    expect(result.pending).toEqual(["answer-1", "code-1"]);
    expect(reloaded.items()).toHaveLength(2);
    expect(reloaded.items().find((item) => item.idempotencyKey === "code-1")?.state).toBe("waiting_runner");
    expect(reloaded.items()[0]?.idempotencyKey).toBe("answer-1");

    const retry = await reloaded.flush(vi.fn(async (input) => String(input).includes("job-1") ? new Response('{"status":"succeeded"}', { status: 200 }) : new Response("{}", { status: 200 })));
    expect(retry.confirmed).toEqual(["answer-1"]);
    expect(reloaded.items()).toHaveLength(1);
    const confirmed = await reloaded.flush(vi.fn(async () => new Response("{}", { status: 200 })));
    expect(confirmed.confirmed).toEqual(["code-1"]);
    expect(reloaded.items()).toEqual([]);
  });

  it.each(["cancelled", "timed_out", "output_overflow", "rejected", "tool_missing"] as const)("persists %s runner jobs as a visible retryable failure instead of polling forever", async (status) => {
    const local = storage();
    const queue = createOfflineDraftQueue(local);
    queue.enqueue({
      kind: "code", url: "/api/runners/submissions", method: "POST", body: { lesson_id: "l1", exercise_id: "l1-c01", source_code: "print(1)" }, idempotencyKey: `code-${status}`,
      state: "waiting_runner", runnerJobId: "terminal-job", scoreIdempotencyKey: `code-${status}:score`,
    });
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ status }), { status: 200, headers: { "content-type": "application/json" } }));

    const result = await queue.flush(fetchMock);

    expect(result.confirmed).toEqual([]);
    expect(result.pending).toEqual([]);
    expect(result.failed).toEqual([`code-${status}`]);
    expect(queue.items()).toMatchObject([{ state: "failed_runner", runnerJobId: "terminal-job", failureReason: status }]);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("keeps the runner job and independent score key after a scoring failure, then removes only after scoring succeeds", async () => {
    const local = storage();
    const queue = createOfflineDraftQueue(local);
    queue.enqueue({
      kind: "code", url: "/api/runners/submissions", method: "POST", body: { lesson_id: "l1", exercise_id: "l1-c01", source_code: "print(1)" }, idempotencyKey: "code-score",
      state: "waiting_runner", runnerJobId: "job-score", scoreIdempotencyKey: "score-key",
    });
    await queue.flush(vi.fn(async () => new Response('{"status":"succeeded"}', { status: 200, headers: { "content-type": "application/json" } })));
    await queue.flush(vi.fn(async () => new Response("temporary", { status: 503 })));

    expect(queue.items()).toMatchObject([{ state: "pending_score", runnerJobId: "job-score", scoreIdempotencyKey: "score-key" }]);
    const confirmed = await queue.flush(vi.fn(async (_input, init) => {
      expect((init?.headers as Record<string, string>)["Idempotency-Key"]).toBe("score-key");
      return new Response("{}", { status: 200, headers: { "content-type": "application/json" } });
    }));
    expect(confirmed.confirmed).toEqual(["code-score"]);
    expect(queue.items()).toEqual([]);
  });

  it("retains queued, running, network-failed, and server-failed jobs for a later flush but stops after a missing job", async () => {
    const local = storage();
    const queue = createOfflineDraftQueue(local);
    for (const [idempotencyKey, runnerJobId] of [["queued", "queued-job"], ["running", "running-job"], ["network", "network-job"], ["missing", "missing-job"]]) {
      queue.enqueue({ kind: "code", url: "/api/runners/submissions", method: "POST", body: { lesson_id: "l1", exercise_id: "l1-c01", source_code: "print(1)" }, idempotencyKey, state: "waiting_runner", runnerJobId });
    }
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const job = String(input).split("/").at(-1);
      if (job === "network-job") throw new TypeError("offline");
      if (job === "missing-job") return new Response("not found", { status: 404 });
      return new Response(JSON.stringify({ status: job === "queued-job" ? "queued" : "running" }), { status: 200, headers: { "content-type": "application/json" } });
    });
    const result = await queue.flush(fetchMock);

    expect(result.pending).toEqual(["queued", "running", "network"]);
    expect(result.failed).toEqual(["missing"]);
    expect(queue.items().find((draft) => draft.idempotencyKey === "missing")).toMatchObject({ state: "failed_runner", failureReason: "runner_not_found" });
    const second = await queue.flush(fetchMock);
    expect(second.failed).toEqual(["missing"]);
    expect(fetchMock.mock.calls.filter(([input]) => String(input).endsWith("missing-job"))).toHaveLength(1);
  });

  it("retries a terminal draft with a new runner key and permits explicit removal", () => {
    const local = storage();
    const queue = createOfflineDraftQueue(local);
    queue.enqueue({ kind: "code", url: "/api/runners/submissions", method: "POST", body: { source_code: "print(1)" }, idempotencyKey: "terminal", state: "failed_runner", runnerJobId: "old-job", scoreIdempotencyKey: "old-score", failureReason: "cancelled" });

    queue.retry("terminal", "terminal-retry");
    expect(queue.items()).toMatchObject([{ idempotencyKey: "terminal-retry", state: "pending_runner" }]);
    expect(queue.items()[0]?.runnerJobId).toBeUndefined();
    queue.remove("terminal-retry");
    expect(queue.items()).toEqual([]);
  });
});
