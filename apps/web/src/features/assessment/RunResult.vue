<script setup lang="ts">
import type { RunView } from "./assessment.store";

defineProps<{ result: RunView | null }>();
const statusLabels: Record<string, string> = { queued: "排队中", running: "运行中", succeeded: "运行完成", failed: "运行失败", cancelled: "已取消", timed_out: "运行超时", output_overflow: "输出超出限制", rejected: "运行请求未通过", tool_missing: "运行服务暂不可用", interrupted: "连接中断" };
</script>

<template>
  <section class="run-result" aria-live="polite">
    <p class="run-result__label">运行结果</p>
    <template v-if="result">
      <h3 :class="{ 'run-result__success': result.status === 'succeeded' }">运行状态：{{ statusLabels[result.status] ?? result.status }}</h3>
      <p v-if="result.status === 'queued' || result.status === 'running'">运行结果将在这里显示，请稍候。</p>
      <p v-else-if="result.status === 'cancelled'">本次运行已取消，可以修改代码后再次运行。</p>
      <p v-else-if="result.status !== 'succeeded'">运行未完成。请根据公开反馈调整后重试。</p>
      <p v-if="result.tests" class="run-result__tests">公开测试：{{ result.tests.visible_passed }} / {{ result.tests.visible_total }} 通过</p>
      <ul v-if="result.diagnostics.length"><li v-for="diagnostic in result.diagnostics" :key="diagnostic">{{ diagnostic }}</li></ul>
    </template>
    <template v-else><h3>等待运行结果</h3><p>写好代码后点击「运行代码」，在这里查看公开测试反馈。</p></template>
  </section>
</template>

<style scoped>
.run-result { min-width: 0; min-height: 15rem; padding: 1.25rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); background: var(--hard-color-space); overflow-wrap: anywhere; }
h3 { margin: .8rem 0; color: var(--hard-color-text); font-size: .95rem; line-height: 1.6; }
p { margin: 0 0 .85rem; color: var(--hard-color-muted); font-size: .8rem; line-height: 1.8; }
.run-result__label { margin: 0; color: var(--hard-color-muted); font-size: .7rem; letter-spacing: .06em; }
.run-result__success { color: var(--hard-color-cyan); }
.run-result__tests { padding-top: 1rem; border-top: 1px solid var(--hard-color-line); color: var(--hard-color-text); }
ul { display: grid; gap: .75rem; margin: 1rem 0 0; padding-left: 1rem; color: var(--hard-color-muted); font: .75rem/1.8 ui-monospace, Consolas, monospace; white-space: pre-wrap; }
</style>
