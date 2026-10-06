<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps<{ modelValue: string; running: boolean }>();
const emit = defineEmits<{ "update:modelValue": [source: string]; run: []; cancel: [] }>();
const panel = ref<"editor" | "result">("editor");
const monacoLanguage = "python";
const monacoHost = ref<HTMLElement>();
const usingTextareaFallback = ref(true);
let editor: { getValue(): string; setValue(value: string): void; onDidChangeModelContent(listener: () => void): { dispose(): void }; dispose(): void } | undefined;
let changeSubscription: { dispose(): void } | undefined;

onMounted(async () => {
  try {
    const monaco = await import("monaco-editor");
    if (!monacoHost.value) return;
    editor = monaco.editor.create(monacoHost.value, {
      value: props.modelValue,
      language: monacoLanguage,
      automaticLayout: true,
      minimap: { enabled: false },
      theme: "vs-dark",
      ariaLabel: "Python 代码编辑器",
    });
    changeSubscription = editor.onDidChangeModelContent(() => emit("update:modelValue", editor?.getValue() ?? ""));
    usingTextareaFallback.value = false;
  } catch {
    usingTextareaFallback.value = true;
  }
});

watch(() => props.modelValue, (value) => {
  if (editor && editor.getValue() !== value) editor.setValue(value);
});
onBeforeUnmount(() => { changeSubscription?.dispose(); editor?.dispose(); });
</script>

<template>
  <section class="code-workspace" data-code-editor :data-language="monacoLanguage" :class="`code-workspace--${panel}`">
    <div class="code-workspace__tabs" aria-label="手机代码面板">
      <button type="button" :aria-pressed="panel === 'editor'" @click="panel = 'editor'">编辑器</button>
      <button type="button" :aria-pressed="panel === 'result'" @click="panel = 'result'">结果</button>
    </div>
    <div class="code-workspace__editor">
      <label>Python 代码编辑器</label>
      <div ref="monacoHost" class="code-workspace__monaco" :class="{ 'code-workspace__monaco--hidden': usingTextareaFallback }"></div>
      <textarea v-if="usingTextareaFallback" id="python-editor" aria-label="Python 代码编辑器" :value="props.modelValue" spellcheck="false" @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"></textarea>
      <p>{{ usingTextareaFallback ? "Monaco 不可用，已切换到 textarea 无障碍降级。" : "Monaco 语言配置：Python。" }}</p>
      <button type="button" :disabled="props.running" @click="emit('run')">运行代码</button>
      <button v-if="props.running" type="button" @click="emit('cancel')">取消运行</button>
    </div>
    <div class="code-workspace__result"><slot name="result" /></div>
  </section>
</template>

<style scoped>
.code-workspace { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 0.85fr); gap: var(--hard-space-3); }
.code-workspace__tabs { display: none; }
.code-workspace__editor { display: grid; gap: var(--hard-space-2); }
.code-workspace__monaco { min-height: 18rem; overflow: hidden; border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); }
.code-workspace__monaco--hidden { display: none; }
textarea { width: 100%; min-height: 18rem; padding: var(--hard-space-3); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); color: var(--hard-color-text); background: var(--hard-color-space); font-family: ui-monospace, Consolas, monospace; font-size: var(--hard-text-md); line-height: 1.5; }
p { margin: 0; color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
button { min-height: var(--hard-touch-target); width: fit-content; padding: 0 var(--hard-space-3); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; cursor: pointer; }

@media (max-width: 52rem) and (orientation: portrait) {
  .code-workspace { display: block; }
  .code-workspace__tabs { display: flex; gap: var(--hard-space-2); margin-bottom: var(--hard-space-3); }
  .code-workspace__tabs button { background: var(--hard-color-surface-raised); }
  .code-workspace__tabs button[aria-pressed="true"] { background: var(--hard-color-primary); }
  .code-workspace--editor .code-workspace__result, .code-workspace--result .code-workspace__editor { display: none; }
}
</style>
