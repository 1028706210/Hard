import { reactive, readonly } from "vue";

import { requestJson } from "../../api/client";
import { enqueueOfflineDraft } from "../../app/offline-drafts";

export interface LessonLink { readonly id: string; readonly title: string; readonly locked: boolean; }
export interface CourseModule { readonly id: string; readonly title: string; readonly prerequisites: readonly string[]; readonly lessons: readonly LessonLink[]; }
export interface Course { readonly language: string; readonly title: string; readonly fixture_only: boolean; readonly modules: readonly CourseModule[]; }
export interface Lesson { id: string; title: string; language?: string; rendered_html: string; source_url: string; source_snapshot_date: string; }
export type SyncStatus = "idle" | "syncing" | "synced" | "failed";

interface StorageLike { getItem(key: string): string | null; setItem(key: string, value: string): void; removeItem(key: string): void; }

const allowedTags = new Set(["P", "H1", "H2", "H3", "H4", "H5", "H6", "UL", "OL", "LI", "PRE", "CODE", "EM", "STRONG", "A", "BLOCKQUOTE"]);

function isAllowedSourceLink(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && url.hostname === "www.runoob.com";
  } catch {
    return false;
  }
}

export function sanitizeLessonHtml(html: string): string {
  const parsed = new DOMParser().parseFromString(html, "text/html");
  for (const element of [...parsed.body.querySelectorAll("*")]) {
    if (element.tagName === "SCRIPT" || element.tagName === "STYLE") {
      element.remove();
      continue;
    }
    if (!allowedTags.has(element.tagName)) {
      element.replaceWith(...element.childNodes);
      continue;
    }
    for (const attribute of [...element.attributes]) {
      if (element.tagName === "A" && attribute.name === "href" && isAllowedSourceLink(attribute.value)) continue;
      element.removeAttribute(attribute.name);
    }
  }
  return parsed.body.innerHTML;
}

function draftKey(lessonId: string) { return `hard:lesson-draft:${lessonId}`; }
function generatedKey() { return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`; }

export function createCourseStore(
  fetchImpl: typeof fetch = fetch,
  storage: StorageLike = localStorage,
  createKey: () => string = generatedKey,
) {
  const state = reactive({
    course: null as Course | null,
    lesson: null as Lesson | null,
    noteDraft: "",
    favorite: false,
    syncStatus: "idle" as SyncStatus,
    error: "",
  });
  let noteKey = "";

  function requireLesson() {
    if (!state.lesson) throw new Error("lesson_not_loaded");
    return state.lesson;
  }

  function setLesson(lesson: Lesson) {
    state.lesson = { ...lesson, rendered_html: sanitizeLessonHtml(lesson.rendered_html) };
    state.noteDraft = storage.getItem(draftKey(lesson.id)) ?? "";
  }

  async function loadCourse(language: string) {
    state.error = "";
    state.course = await requestJson<Course>(`/api/content/courses/${language}`, undefined, fetchImpl);
  }

  async function loadLesson(lessonId: string) {
    state.error = "";
    const lesson = await requestJson<Lesson>(`/api/content/lessons/${lessonId}`, undefined, fetchImpl);
    setLesson(lesson);
  }

  function setNoteDraft(body: string) {
    state.noteDraft = body;
  }

  async function saveNote() {
    const lesson = requireLesson();
    const key = noteKey || (noteKey = createKey());
    state.syncStatus = "syncing";
    try {
      await requestJson(`/api/progress/notes/${lesson.id}`, {
        method: "PUT",
        headers: { "content-type": "application/json", "Idempotency-Key": key },
        body: JSON.stringify({ body: state.noteDraft }),
      }, fetchImpl);
      storage.removeItem(draftKey(lesson.id));
      state.syncStatus = "synced";
      noteKey = "";
    } catch (error) {
      storage.setItem(draftKey(lesson.id), state.noteDraft);
      enqueueOfflineDraft({ kind: "note", url: `/api/progress/notes/${lesson.id}`, method: "PUT", body: { body: state.noteDraft }, idempotencyKey: key }, storage);
      state.syncStatus = "failed";
      throw error;
    }
  }

  async function retryNote() { return saveNote(); }

  async function saveProgress(position: number, timeSpentSeconds: number) {
    const lesson = requireLesson();
    const idempotencyKey = createKey();
    const request = {
      method: "PATCH",
      headers: { "content-type": "application/json", "Idempotency-Key": idempotencyKey },
      body: JSON.stringify({ position, time_spent_seconds: timeSpentSeconds }),
    } as const;
    try { return await requestJson(`/api/progress/lessons/${lesson.id}`, request, fetchImpl); }
    catch (error) { enqueueOfflineDraft({ kind: "progress", url: `/api/progress/lessons/${lesson.id}`, method: "PATCH", body: { position, time_spent_seconds: timeSpentSeconds }, idempotencyKey }, storage); throw error; }
  }

  async function setFavorite(favorite: boolean) {
    const lesson = requireLesson();
    await requestJson(`/api/progress/favorites/${lesson.id}`, {
      method: favorite ? "PUT" : "DELETE",
      headers: { "Idempotency-Key": createKey() },
    }, fetchImpl);
    state.favorite = favorite;
  }

  return { state: readonly(state), loadCourse, loadLesson, setLesson, setNoteDraft, saveNote, retryNote, saveProgress, setFavorite };
}

export const courseStore = createCourseStore();
