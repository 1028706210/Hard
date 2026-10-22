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
  status.value = ""; error.value = "";
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
    <header><p>让学习环境，适合自己的节奏</p><h1 id="settings-title">设置与数据</h1><p class="page-intro">管理每日目标、保护学习记录，连接你的其他设备。</p></header>
    <p v-if="error" class="notice notice--error" role="alert">{{ error }}</p>
    <div class="settings-layout">
      <nav class="settings-nav" aria-label="设置分区"><p>偏好与管理</p><a href="#learning-goal"><span>01</span>每日目标</a><a href="#learning-data"><span>02</span>数据管理</a><a href="#phone-access"><span>03</span>手机访问</a><a href="#runtime-health"><span>04</span>运行环境</a><small>学习记录保存在本机。<br>定期导出，为积累留一份备份。</small></nav>
      <div class="settings-content">
        <section id="learning-goal" class="panel"><span class="section-kicker">01 · 学习偏好</span><h2>每日目标</h2><p>设定适合自己的步调，随时可以调整。</p><form @submit.prevent="saveGoal"><label>每日学习分钟<div class="number-field"><input v-model.number="minutes" aria-label="每日学习分钟" type="number" min="0"><span>分钟 / 天</span></div></label><label>每日练习数量<div class="number-field"><input v-model.number="exercises" aria-label="每日练习数量" type="number" min="0"><span>题 / 天</span></div></label><button type="submit">保存目标</button></form><p v-if="status" class="notice notice--success" role="status">{{ status }}</p></section>
        <section id="learning-data" class="panel"><span class="section-kicker">02 · 备份与恢复</span><DataManagement /></section>
        <section id="phone-access" class="panel"><span class="section-kicker">03 · 设备连接</span><LanAccess /></section>
        <section id="runtime-health" class="panel"><span class="section-kicker">04 · 本机状态</span><h2>运行环境</h2><p>{{ Object.values(checks).filter(check => check.healthy).length }} / {{ Object.keys(checks).length }} 项检查正常</p><details><summary>查看工具健康与本机路径</summary><ul class="checks"><li v-for="(check, name) in checks" :key="name"><span :class="check.healthy ? 'healthy' : 'unhealthy'">{{ check.healthy ? "健康" : "需要注意" }}</span><strong>{{ name }}</strong><code>{{ check.path ?? check.detail ?? "未提供路径" }}</code></li></ul></details></section>
      </div>
    </div>
  </section>
</template>

<style scoped>
.settings-page { display: grid; overflow-wrap: anywhere; gap: var(--hard-space-5); max-width: 70rem; margin: 0 auto; } header p { margin: 0; color: var(--hard-color-primary-strong); } h1 { margin: var(--hard-space-1) 0 0; font-size: clamp(2rem, 5vw, 3.5rem); } h2 { margin: 0; font-size: var(--hard-text-lg); } .panel { display: grid; gap: var(--hard-space-3); padding: var(--hard-space-4); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); } .panel p { margin: 0; color: var(--hard-color-muted); line-height: 1.65; } .panel strong { color: var(--hard-color-amber); }
.checks { display: grid; gap: var(--hard-space-2); padding: 0; margin: 0; list-style: none; } .checks li { display: grid; grid-template-columns: auto minmax(6rem, 1fr) minmax(0, 2fr); gap: var(--hard-space-3); align-items: center; padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); background: var(--hard-color-surface-raised); } .healthy { color: var(--hard-color-cyan); } .unhealthy { color: var(--hard-color-danger); } code { min-width: 0; overflow-wrap: anywhere; color: var(--hard-color-muted); }
form { display: grid; grid-template-columns: 1fr 1fr auto; gap: var(--hard-space-3); align-items: end; } label { display: grid; gap: var(--hard-space-1); color: var(--hard-color-muted); font-size: var(--hard-text-sm); } input { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-space); font: inherit; } button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; cursor: pointer; } button:disabled { cursor: not-allowed; opacity: .55; } .notice { margin: 0; padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); } .notice--success { color: var(--hard-color-cyan); background: color-mix(in srgb, var(--hard-color-cyan) 12%, transparent); } .notice--error { color: var(--hard-color-danger); background: color-mix(in srgb, var(--hard-color-danger) 12%, transparent); }
@media (max-width: 42rem) { .checks li, form { grid-template-columns: 1fr; align-items: start; } }
summary { min-height: 44px; padding: .75rem 0; color: var(--hard-color-primary-strong); } details[open] summary { margin-bottom: 1rem; }
.panel { padding: 1.5rem; gap: 1.25rem; }
form { max-width: 52rem; }
form label { gap: .65rem; }
input { width: 100%; min-width: 0; }
.checks li { background: transparent; border-bottom: 1px solid var(--hard-color-line); border-radius: 0; }
@media (max-width: 42rem) { .panel { padding: 1.25rem; } }
.page-intro { margin-top: .85rem; color: var(--hard-color-muted); line-height: 1.8; }
.settings-layout { display: grid; grid-template-columns: 12rem minmax(0, 1fr); gap: 2rem; align-items: start; }
.settings-nav { position: sticky; top: 6rem; display: grid; gap: .4rem; }
.settings-nav p { margin: 0 0 .75rem; padding-left: .85rem; color: var(--hard-color-muted); font-size: .75rem; }
.settings-nav a { display: flex; align-items: center; gap: .85rem; min-height: var(--hard-touch-target); padding: .75rem .85rem; border: 1px solid transparent; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); text-decoration: none; font-size: .875rem; }
.settings-nav a:hover { border-color: var(--hard-color-line); background: var(--hard-color-surface); }
.settings-nav a span { color: var(--hard-color-cyan); font: .7rem ui-monospace, monospace; }
.settings-nav small { margin-top: 1.5rem; padding: 1rem .85rem; border-top: 1px solid var(--hard-color-line); color: var(--hard-color-muted); font-size: .75rem; line-height: 1.9; }
.settings-content { display: grid; min-width: 0; gap: 1.5rem; }
.settings-content > section { scroll-margin-top: 7rem; }
.section-kicker { color: var(--hard-color-primary-strong); font-size: .75rem; letter-spacing: .04em; }
.panel { gap: 1rem; padding: clamp(1.25rem, 3vw, 2rem); }
.panel h2 { font-size: 1.3rem; }
form { grid-template-columns: 1fr 1fr; align-items: end; margin-top: .25rem; }
form > button { justify-self: start; grid-column: 1 / -1; padding-inline: 1.25rem; }
.number-field { position: relative; }
.number-field input { padding-right: 6rem; }
.number-field span { position: absolute; inset: 0 .9rem 0 auto; display: flex; align-items: center; pointer-events: none; font-size: .75rem; }
.checks li { grid-template-columns: auto minmax(0, 1fr); }
.checks code { grid-column: 1 / -1; }
.checks strong { color: var(--hard-color-text); }
@media (max-width: 58rem) { .settings-layout { grid-template-columns: 1fr; gap: 1.5rem; } .settings-nav { position: static; display: flex; flex-wrap: wrap; gap: .5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--hard-color-line); } .settings-nav p, .settings-nav small { display: none; } .settings-nav a { border-color: var(--hard-color-line); } }
@media (max-width: 35rem) { form { grid-template-columns: 1fr; } .settings-nav a { padding: .65rem .8rem; } }
</style>
