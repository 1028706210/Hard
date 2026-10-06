<script setup lang="ts">
import { ref, watch } from "vue";

import type { Exercise, RunView } from "./assessment.store";
import CodeWorkspace from "./CodeWorkspace.vue";
import RunResult from "./RunResult.vue";

const props = defineProps<{ exercise: Exercise; result: RunView | null; running: boolean }>();
const emit = defineEmits<{ run: [source: string]; cancel: [] }>();
const source = ref(props.exercise.starter_code ?? "");
watch(() => props.exercise.id, () => { source.value = props.exercise.starter_code ?? ""; });
</script>

<template>
  <section class="code-exercise">
    <p>{{ props.exercise.prompt }}</p>
    <CodeWorkspace v-model="source" :running="props.running" @run="emit('run', source)" @cancel="emit('cancel')">
      <template #result><RunResult :result="props.result" /></template>
    </CodeWorkspace>
  </section>
</template>

<style scoped>
.code-exercise { display: grid; gap: var(--hard-space-3); }
.code-exercise > p { margin: 0; color: var(--hard-color-muted); }
</style>
