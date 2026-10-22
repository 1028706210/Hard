<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import type { editor as MonacoEditor } from "monaco-editor";

const props = defineProps<{ modelValue: string; language: string; running: boolean }>();
const emit = defineEmits<{ "update:modelValue": [source: string]; run: []; cancel: [] }>();
const panel = ref<"editor" | "result">("editor");
const editorSemanticsByLanguage: Record<string, { monacoLanguage: string; label: string; id: string }> = {
  python: { monacoLanguage: "python", label: "Python 代码编辑器", id: "python-editor" },
  java: { monacoLanguage: "java", label: "Java 代码编辑器", id: "java-editor" },
  csharp: { monacoLanguage: "csharp", label: "C# 代码编辑器", id: "csharp-editor" },
  cpp: { monacoLanguage: "cpp", label: "C++ 代码编辑器", id: "cpp-editor" },
  plaintext: { monacoLanguage: "plaintext", label: "纯文本代码编辑器", id: "plaintext-editor" },
};
const editorSemantics = computed(() => editorSemanticsByLanguage[props.language] ?? editorSemanticsByLanguage.plaintext!);
const monacoHost = ref<HTMLElement>();
const usingTextareaFallback = ref(true);
let editor: MonacoEditor.IStandaloneCodeEditor | undefined;
let changeSubscription: { dispose(): void } | undefined;
let setModelLanguage: ((model: MonacoEditor.ITextModel, language: string) => void) | undefined;

onMounted(async () => {
  try {
    const monaco = await import("monaco-editor");
    if (!monacoHost.value) return;
    editor = monaco.editor.create(monacoHost.value, {
      value: props.modelValue,
      language: editorSemantics.value.monacoLanguage,
      automaticLayout: true,
      minimap: { enabled: false },
      theme: "vs-dark",
      ariaLabel: editorSemantics.value.label,
      fontSize: 14,
      lineHeight: 24,
      padding: { top: 16, bottom: 16 },
      scrollBeyondLastLine: false,
      renderLineHighlight: "none",
    });
    setModelLanguage = monaco.editor.setModelLanguage;
    changeSubscription = editor.onDidChangeModelContent(() => emit("update:modelValue", editor?.getValue() ?? ""));
    usingTextareaFallback.value = false;
  } catch {
    usingTextareaFallback.value = true;
  }
});

watch(() => props.modelValue, (value) => {
  if (editor && editor.getValue() !== value) editor.setValue(value);
});
watch(() => editorSemantics.value.monacoLanguage, (language) => {
  const model = editor?.getModel();
  if (model && setModelLanguage) setModelLanguage(model, language);
  editor?.updateOptions({ ariaLabel: editorSemantics.value.label });
});
onBeforeUnmount(() => { changeSubscription?.dispose(); editor?.dispose(); });
</script>

<template>
  <section class="code-workspace" data-code-editor :data-language="editorSemantics.monacoLanguage" :class="`code-workspace--${panel}`">
    <div class="code-workspace__tabs" aria-label="手机代码面板">
      <button type="button" :aria-pressed="panel === 'editor'" @click="panel = 'editor'">编辑器</button>
      <button type="button" :aria-pressed="panel === 'result'" @click="panel = 'result'">结果</button>
    </div>
    <div class="code-workspace__editor">
      <div class="code-workspace__heading"><label :for="editorSemantics.id">{{ editorSemantics.label }}</label><span>{{ props.language === 'csharp' ? 'C#' : props.language === 'cpp' ? 'C++' : props.language }}</span></div>
      <div ref="monacoHost" class="code-workspace__monaco" :class="{ 'code-workspace__monaco--hidden': usingTextareaFallback }"></div>
      <textarea v-if="usingTextareaFallback" :id="editorSemantics.id" :aria-label="editorSemantics.label" :value="props.modelValue" spellcheck="false" @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"></textarea>
      <p>{{ usingTextareaFallback ? "正在使用基础编辑模式，你可以正常编写与运行代码。" : "编写代码后运行，查看公开测试与诊断。" }}</p>
      <div class="code-workspace__actions"><button type="button" :disabled="props.running" :aria-busy="props.running" @click="emit('run')">运行代码</button>
      <button v-if="props.running" class="code-workspace__cancel" type="button" @click="emit('cancel')">取消运行</button></div>
    </div>
    <div class="code-workspace__result"><slot name="result" /></div>
  </section>
</template>

<style scoped>
.code-workspace { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, .85fr); gap: 1rem; align-items: start; }
.code-workspace__tabs { display: none; }
.code-workspace__editor { display: grid; gap: .8rem; min-width: 0; }
.code-workspace__heading { display: flex; align-items: center; justify-content: space-between; gap: .75rem; min-height: 30px; }
.code-workspace__heading label { color: var(--hard-color-text); font-size: .8rem; font-weight: 600; }
.code-workspace__heading span { padding: .15rem .45rem; border: 1px solid var(--hard-color-line); border-radius: .3rem; color: var(--hard-color-muted); font: .65rem ui-monospace, monospace; text-transform: uppercase; }
.code-workspace__actions { display: flex; flex-wrap: wrap; gap: .75rem; padding-top: .25rem; }
.code-workspace__actions > button:first-child { min-width: 8rem; }
.code-workspace__actions .code-workspace__cancel { background: transparent; border: 1px solid var(--hard-color-line); }
.code-workspace__monaco { height: 22rem; min-height: 18rem; overflow: hidden; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); }
.code-workspace__monaco--hidden { display: none; }
textarea { width: 100%; min-height: 22rem; resize: vertical; padding: 1rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-space); font-family: ui-monospace, Consolas, monospace; font-size: .875rem; line-height: 1.75; tab-size: 4; }
p { margin: 0; color: var(--hard-color-muted); font-size: .72rem; line-height: 1.7; }
button { min-height: var(--hard-touch-target); width: fit-content; padding: 0 var(--hard-space-3); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; cursor: pointer; }
button:disabled { opacity: .55; cursor: wait; }
.code-workspace__result { min-width: 0; padding-top: 2.65rem; }

@media (min-width: 52.01rem) and (max-width: 68rem) { .code-workspace { grid-template-columns: 1fr; } .code-workspace__result { padding-top: 0; } }
@media (max-width: 52rem) {
  .code-workspace { display: block; }
  .code-workspace__tabs { display: flex; gap: .35rem; margin-bottom: 1rem; padding: .3rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); background: var(--hard-color-space); }
  .code-workspace__tabs button { flex: 1; background: transparent; color: var(--hard-color-muted); font-size: .85rem; }
  .code-workspace__tabs button[aria-pressed="true"] { background: var(--hard-color-surface-raised); color: var(--hard-color-text); }
  .code-workspace__result { padding-top: 0; }
  .code-workspace__monaco { height: 20rem; }
  textarea { min-height: 20rem; }
  .code-workspace--editor .code-workspace__result, .code-workspace--result .code-workspace__editor { display: none; }
}
</style>
