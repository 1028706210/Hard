<script setup lang="ts">
import { nextTick, ref, watch } from "vue";

import type { Exercise, RunView } from "./assessment.store";
import CodeWorkspace from "./CodeWorkspace.vue";
import RunResult from "./RunResult.vue";
import { clearEditorDraft, loadEditorDraft, saveEditorDraft, type EditorDraftStorage } from "./editor-drafts";

const props = withDefaults(defineProps<{ lessonId: string; language: string; exercise: Exercise; result: RunView | null; running: boolean; storage?: EditorDraftStorage }>(), { storage: () => localStorage });
const emit = defineEmits<{ run: [source: string]; cancel: [] }>();
const source = ref("");
const draftKey = ref("");
const restoredDraft = ref(false);
let clearingDraft = false;

function createDraftKey() { return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`; }
function restoreDraft() {
  const draft = loadEditorDraft(props.storage, props.lessonId, props.exercise.id);
  source.value = draft?.sourceCode ?? props.exercise.starter_code ?? "";
  draftKey.value = draft?.idempotencyKey ?? "";
  restoredDraft.value = !!draft;
}
function clearDraft() {
  clearingDraft = true;
  clearEditorDraft(props.storage, props.lessonId, props.exercise.id);
  source.value = props.exercise.starter_code ?? "";
  draftKey.value = "";
  restoredDraft.value = false;
  void nextTick(() => { clearingDraft = false; });
}
restoreDraft();
watch(() => [props.lessonId, props.exercise.id], restoreDraft);
watch(source, (value) => {
  if (clearingDraft) return;
  const existing = loadEditorDraft(props.storage, props.lessonId, props.exercise.id);
  draftKey.value = existing?.sourceCode === value ? existing.idempotencyKey : createDraftKey();
  saveEditorDraft(props.storage, props.lessonId, props.exercise.id, value, draftKey.value);
});
</script>

<template>
  <section class="code-exercise">
    <p>{{ props.exercise.prompt }}</p>
    <details v-if="props.exercise.visible_tests.length" class="code-exercise__tests"><summary>公开测试 <span>{{ props.exercise.visible_tests.length }}</span></summary><ul><li v-for="(test, index) in props.exercise.visible_tests" :key="index"><code>{{ test }}</code></li></ul></details>
    <p v-if="restoredDraft" class="code-exercise__draft-status" role="status">已恢复本地草稿。</p>
    <CodeWorkspace v-model="source" :language="props.language" :running="props.running" @run="emit('run', source)" @cancel="emit('cancel')">
      <template #result><RunResult :result="props.result" /></template>
    </CodeWorkspace>
    <button data-clear-draft type="button" @click="clearDraft">清除本地草稿</button>
  </section>
</template>

<style scoped>
.code-exercise { display: grid; gap: 1.25rem; }
.code-exercise > p { margin: 0; color: var(--hard-color-text); font-size: 1.05rem; line-height: 1.85; }
.code-exercise > .code-exercise__draft-status { padding: .65rem .9rem; border-left: 2px solid var(--hard-color-cyan); background: var(--hard-color-space); color: var(--hard-color-muted); font-size: .8rem; }
.code-exercise__tests { border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); background: var(--hard-color-space); }
.code-exercise__tests summary { min-height: 44px; padding: .75rem 1rem; color: var(--hard-color-muted); font-size: .8rem; cursor: pointer; }
.code-exercise__tests summary span { margin-left: .5rem; font-family: ui-monospace, monospace; }
.code-exercise__tests ul { margin: 0; padding: 0 1rem 1rem 2rem; color: var(--hard-color-muted); line-height: 1.8; }
.code-exercise__tests code { font-size: .8rem; overflow-wrap: anywhere; white-space: pre-wrap; }
.code-exercise > button { justify-self: start; min-height: var(--hard-touch-target); width: fit-content; padding: .5rem 0; border: 0; color: var(--hard-color-muted); background: transparent; font: inherit; font-size: .75rem; text-decoration: underline; text-decoration-color: var(--hard-color-line); text-underline-offset: .3rem; cursor: pointer; }
.code-exercise > button:hover { color: var(--hard-color-text); }
</style>
