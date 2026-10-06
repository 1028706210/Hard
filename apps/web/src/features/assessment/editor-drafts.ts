interface StorageLike { getItem(key: string): string | null; setItem(key: string, value: string): void; removeItem(key: string): void; }

export interface EditorDraft { sourceCode: string; idempotencyKey: string; }

function key(lessonId: string, exerciseId: string) { return `hard:editor-draft:${lessonId}:${exerciseId}`; }

export function loadEditorDraft(storage: StorageLike, lessonId: string, exerciseId: string): EditorDraft | null {
  const value = storage.getItem(key(lessonId, exerciseId));
  if (!value) return null;
  try {
    const draft = JSON.parse(value) as EditorDraft;
    return typeof draft.sourceCode === "string" && typeof draft.idempotencyKey === "string" ? draft : null;
  } catch {
    storage.removeItem(key(lessonId, exerciseId));
    return null;
  }
}

export function saveEditorDraft(storage: StorageLike, lessonId: string, exerciseId: string, sourceCode: string, idempotencyKey: string) {
  storage.setItem(key(lessonId, exerciseId), JSON.stringify({ sourceCode, idempotencyKey } satisfies EditorDraft));
}
