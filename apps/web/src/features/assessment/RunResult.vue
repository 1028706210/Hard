<script setup lang="ts">
import type { RunView } from "./assessment.store";

defineProps<{ result: RunView | null }>();
</script>

<template>
  <section class="run-result" aria-live="polite">
    <template v-if="result">
      <h3>运行状态：{{ result.status }}</h3>
      <p>耗时：{{ result.duration_ms }}ms</p>
      <p>隐藏测试失败：{{ result.hidden_test_failures }}</p>
      <pre v-if="result.stdout">{{ result.stdout }}</pre>
      <ul v-if="result.diagnostics.length"><li v-for="diagnostic in result.diagnostics" :key="diagnostic">{{ diagnostic }}</li></ul>
    </template>
    <p v-else>等待运行结果</p>
  </section>
</template>

<style scoped>
.run-result { min-width: 0; padding: var(--hard-space-4); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-space); }
h3, p { margin-top: 0; } p { color: var(--hard-color-muted); }
pre { overflow-x: auto; white-space: pre-wrap; overflow-wrap: anywhere; color: var(--hard-color-cyan); }
</style>
