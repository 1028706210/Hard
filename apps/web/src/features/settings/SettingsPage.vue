<script setup lang="ts">
import { onMounted, ref } from "vue";

import { requestJson } from "../../api/client";
import DataManagement from "./DataManagement.vue";
import LanAccess from "./LanAccess.vue";

interface Check { healthy: boolean; path?: string; detail?: string; }
interface Goal { target_minutes: number; target_exercises: number; }
const checks = ref<Record<string, Check>>({});
const minutes = ref(0);
const exercises = ref(0);
const status = ref("");
const error = ref("");

function key() { return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-goal`; }
async function load() {
  try {
    const [health, summary] = await Promise.all([
      requestJson<{ checks: Record<string, Check> }>("/api/v1/health/ready"),
      requestJson<{ daily_goal: Goal }>("/api/progress/summary"),
    ]);
    checks.value = health.checks;
    minutes.value = summary.daily_goal.target_minutes;
    exercises.value = summary.daily_goal.target_exercises;
  } catch { error.value = "本机设置暂时无法读取。"; }
}
async function saveGoal() {
  status.value = "";
  try {
    const saved = await requestJson<Goal>("/api/progress/daily-goal", {
      method: "PUT",
      headers: { "content-type": "application/json", "Idempotency-Key": key() },
      body: JSON.stringify({ target_minutes: Number(minutes.value), target_exercises: Number(exercises.value) }),
    });
    minutes.value = saved.target_minutes;
    exercises.value = saved.target_exercises;
    status.value = "目标已保存";
  } catch { error.value = "目标尚未保存，请重试。"; }
}

onMounted(load);
</script>

<template>
  <section class="settings-page" aria-labelledby="settings-title">
    <header><p>本机数据与学习偏好</p><h1 id="settings-title">设置与数据</h1></header>
    <p v-if="error" class="notice notice--error" role="alert">{{ error }}</p>
    <section class="panel"><h2>D 盘工具健康</h2><ul class="checks"><li v-for="(check, name) in checks" :key="name"><span :class="check.healthy ? 'healthy' : 'unhealthy'">{{ check.healthy ? "健康" : "需要注意" }}</span><strong>{{ name }}</strong><code>{{ check.path ?? check.detail ?? "未提供路径" }}</code></li></ul></section>
    <section class="panel"><h2>每日目标</h2><form @submit.prevent="saveGoal"><label>每日学习分钟<input v-model.number="minutes" aria-label="每日学习分钟" type="number" min="0"></label><label>每日练习数量<input v-model.number="exercises" aria-label="每日练习数量" type="number" min="0"></label><button type="submit">保存目标</button></form><p v-if="status" class="notice notice--success" role="status">{{ status }}</p></section>
    <section class="panel"><DataManagement /></section>
    <section class="panel"><LanAccess /></section>
  </section>
</template>

<style scoped>
.settings-page { display: grid; gap: var(--hard-space-5); max-width: 70rem; margin: 0 auto; } header p { margin: 0; color: var(--hard-color-primary-strong); } h1 { margin: var(--hard-space-1) 0 0; font-size: clamp(2rem, 5vw, 3.5rem); } h2 { margin: 0; font-size: var(--hard-text-lg); } .panel { display: grid; gap: var(--hard-space-3); padding: var(--hard-space-4); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); } .panel p { margin: 0; color: var(--hard-color-muted); line-height: 1.65; } .panel strong { color: var(--hard-color-amber); }
.checks { display: grid; gap: var(--hard-space-2); padding: 0; margin: 0; list-style: none; } .checks li { display: grid; grid-template-columns: auto minmax(6rem, 1fr) minmax(0, 2fr); gap: var(--hard-space-3); align-items: center; padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); background: var(--hard-color-surface-raised); } .healthy { color: var(--hard-color-cyan); } .unhealthy { color: var(--hard-color-danger); } code { min-width: 0; overflow-wrap: anywhere; color: var(--hard-color-muted); }
form { display: grid; grid-template-columns: 1fr 1fr auto; gap: var(--hard-space-3); align-items: end; } label { display: grid; gap: var(--hard-space-1); color: var(--hard-color-muted); font-size: var(--hard-text-sm); } input { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-space); font: inherit; } button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; cursor: pointer; } button:disabled { cursor: not-allowed; opacity: .55; } .notice { margin: 0; padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); } .notice--success { color: var(--hard-color-cyan); background: color-mix(in srgb, var(--hard-color-cyan) 12%, transparent); } .notice--error { color: var(--hard-color-danger); background: color-mix(in srgb, var(--hard-color-danger) 12%, transparent); }
@media (max-width: 42rem) { .checks li, form { grid-template-columns: 1fr; align-items: start; } }
</style>
