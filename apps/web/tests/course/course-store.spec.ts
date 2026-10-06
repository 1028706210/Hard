import { describe, expect, it, vi } from "vitest";

import { createCourseStore, sanitizeLessonHtml } from "../../src/features/course/course.store";


function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
}


function memoryStorage() {
  const values = new Map<string, string>();
  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => values.set(key, value),
    removeItem: (key: string) => values.delete(key),
  };
}


const course = {
  language: "python",
  title: "Python",
  fixture_only: true,
  modules: [{
    id: "python-foundations",
    title: "Python 基础",
    prerequisites: [],
    lessons: [
      { id: "python-foundations-hello-world", title: "Hello World", locked: false },
      { id: "python-foundations-output", title: "输出", locked: true },
    ],
  }],
};


describe("course store", () => {
  it("loads module navigation and keeps prerequisite-locked lessons unavailable", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(json(course));
    const store = createCourseStore(fetchImpl, memoryStorage());

    await store.loadCourse("python");

    expect(store.state.course?.modules[0]?.lessons[0]?.locked).toBe(false);
    expect(store.state.course?.modules[0]?.lessons[1]?.locked).toBe(true);
    expect(fetchImpl).toHaveBeenCalledWith("/api/content/courses/python", {});
  });

  it("stores failed note drafts locally and retries with the original idempotency key", async () => {
    const storage = memoryStorage();
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(json({ error: { code: "offline" } }, 503))
      .mockResolvedValueOnce(json({ lesson_id: "python-foundations-hello-world", body: "我的笔记", updated_at: "now" }));
    const store = createCourseStore(fetchImpl, storage, () => "note-key-1");

    store.setLesson({ id: "python-foundations-hello-world", title: "Hello World", rendered_html: "<p>正文</p>", source_url: "https://www.runoob.com/python3/python3-hello-world.html", source_snapshot_date: "2026-08-23" });
    store.setNoteDraft("我的笔记");
    await expect(store.saveNote()).rejects.toThrow("API request failed");

    expect(store.state.syncStatus).toBe("failed");
    expect(storage.getItem("hard:lesson-draft:python-foundations-hello-world")).toContain("我的笔记");
    await store.retryNote();
    expect(store.state.syncStatus).toBe("synced");
    expect(fetchImpl.mock.calls[0]?.[1]).toMatchObject({ headers: { "Idempotency-Key": "note-key-1" } });
    expect(fetchImpl.mock.calls[1]?.[1]).toMatchObject({ headers: { "Idempotency-Key": "note-key-1" } });
  });

  it("uses idempotent progress and favorite writes without retaining unsafe lesson HTML", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(json({ lesson_id: "python-foundations-hello-world", position: 8, time_spent_seconds: 4, status: "in_progress", updated_at: "now" }))
      .mockResolvedValueOnce(json({ lesson_id: "python-foundations-hello-world", favorite: true }));
    const store = createCourseStore(fetchImpl, memoryStorage(), () => "write-key-1");

    store.setLesson({ id: "python-foundations-hello-world", title: "Hello World", rendered_html: "<p>正文</p>", source_url: "https://www.runoob.com/python3/python3-hello-world.html", source_snapshot_date: "2026-08-23" });
    await store.saveProgress(8, 4);
    await store.setFavorite(true);

    expect(fetchImpl.mock.calls.map(([input]) => input)).toEqual([
      "/api/progress/lessons/python-foundations-hello-world",
      "/api/progress/favorites/python-foundations-hello-world",
    ]);
    expect(fetchImpl.mock.calls.every(([, init]) => new Headers((init as RequestInit).headers).get("Idempotency-Key") === "write-key-1")).toBe(true);
    expect(sanitizeLessonHtml('<p>安全</p><script>bad()</script><a href="javascript:bad()">坏链接</a><a href="https://example.com">未审核</a><a href="https://www.runoob.com/python3/">来源</a>')).toBe("<p>安全</p><a>坏链接</a><a>未审核</a><a href=\"https://www.runoob.com/python3/\">来源</a>");
  });
});
