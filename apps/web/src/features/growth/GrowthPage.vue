<script setup lang="ts">
import { onMounted, ref } from "vue";

import { requestJson, type GrowthSummaryResponse } from "../../api/client";

interface Summary extends GrowthSummaryResponse { total_experience: number; level: number; current_level_progress: number; next_level_remaining: number; streak_days: number; badges: string[]; mastery: Array<{ scope_type: string; scope_id: string; score: number }>; }
interface HistoryItem { id: string; exercise_id: string; language: string | null; source_code: string; normalized_result: Record<string, unknown>; score: number; duration_ms: number | null; created_at: string; diff: string; }
interface Weakness { concept_id: string; score: number; lesson_id: string; exercise_id: string; }

const summary = ref<Summary | null>(null);
const history = ref<HistoryItem[]>([]);
const weaknesses = ref<Weakness[]>([]);
const error = ref("");
const scopeLabels: Record<string, string> = { lesson: "课时", module: "模块", course: "课程" };
function scopeLabel(scope: string) { return scopeLabels[scope] ?? "学习范围"; }

async function load() {
  try {
    const [growth, codeHistory, weak] = await Promise.all([
      requestJson<Summary>("/api/growth/summary"),
      requestJson<{ items: HistoryItem[] }>("/api/growth/history"),
      requestJson<{ items: Weakness[] }>("/api/growth/weaknesses"),
    ]);
    summary.value = growth;
    history.value = codeHistory.items;
    weaknesses.value = weak.items;
  } catch { error.value = "成长数据暂时无法读取。"; }
}

onMounted(load);
</script>

<template>
  <section class="growth-page" aria-labelledby="growth-title">
    <header><p>只呈现真实学习记录</p><h1 id="growth-title">成长报告</h1></header>
    <p v-if="error" class="notice" role="alert">{{ error }}</p>
    <template v-else-if="summary">
      <section class="metrics" aria-label="成长概览"><div><span>经验</span><strong>{{ summary.total_experience }} XP</strong></div><div><span>等级</span><strong>{{ summary.level }}</strong></div><div><span>连续学习</span><strong>{{ summary.streak_days }} 天</strong></div><div><span>下级还需</span><strong>{{ summary.next_level_remaining }} XP</strong></div></section>
      <section class="panel"><h2>徽章与掌握度</h2><p v-if="!summary.badges.length" class="empty-state">尚未获得徽章。</p><ul v-else class="badges"><li v-for="badge in summary.badges" :key="badge">{{ badge }}</li></ul><p v-if="!summary.mastery.length" class="empty-state">尚无掌握度记录。</p><ul v-else class="mastery"><li v-for="item in summary.mastery" :key="`${item.scope_type}-${item.scope_id}`" data-mastery-record><span>{{ scopeLabel(item.scope_type) }} · {{ item.scope_id }}</span><strong>{{ item.score }}%</strong></li></ul></section>
      <section class="panel"><h2>学习热力图</h2><p class="empty-state">热力图数据尚不可用；这里不会生成虚假的学习记录。</p></section>
      <section class="panel"><h2>弱点链接</h2><p v-if="!weaknesses.length" class="empty-state">没有近期弱点。</p><ul v-else class="weaknesses"><li v-for="item in weaknesses" :key="`${item.concept_id}-${item.exercise_id}`"><a data-weakness-link :href="`/assessment/${item.lesson_id}`">{{ item.concept_id }}</a><span>分数 {{ item.score }} · {{ item.exercise_id }}</span></li></ul></section>
      <section class="panel"><h2>代码成长历史</h2><p v-if="!history.length" class="empty-state">尚无代码提交历史。</p><article v-for="item in history" v-else :key="item.id" class="history"><header><strong>{{ item.exercise_id }}</strong><span>{{ item.language ?? "未知语言" }} · {{ item.score }} 分 · {{ item.created_at }}</span></header><h3>源码</h3><pre data-plain-text="source">{{ item.source_code }}</pre><h3>与上一份提交的差异</h3><pre data-plain-text="diff">{{ item.diff }}</pre></article></section>
    </template>
    <p v-else class="empty-state">正在读取成长数据。</p>
  </section>
</template>

<style scoped>
.growth-page { display: grid; gap: var(--hard-space-5); max-width: 76rem; margin: 0 auto; } header p { margin: 0; color: var(--hard-color-primary-strong); } h1 { margin: var(--hard-space-1) 0 0; font-size: clamp(2rem, 5vw, 3.5rem); } h2 { margin: 0; font-size: var(--hard-text-lg); } h3 { margin: var(--hard-space-4) 0 var(--hard-space-2); color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
.metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--hard-space-3); } .metrics div, .panel { padding: var(--hard-space-4); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); } .metrics span, .history header span { display: block; color: var(--hard-color-muted); font-size: var(--hard-text-sm); } .metrics strong { display: block; margin-top: var(--hard-space-2); color: var(--hard-color-cyan); font-size: var(--hard-text-xl); }
.panel { display: grid; gap: var(--hard-space-3); } .badges, .mastery, .weaknesses { display: grid; gap: var(--hard-space-2); padding: 0; margin: 0; list-style: none; } .badges { grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr)); } .badges li, .mastery li, .weaknesses li { padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); background: var(--hard-color-surface-raised); } .mastery li, .weaknesses li { display: flex; justify-content: space-between; gap: var(--hard-space-3); } .weaknesses a { color: var(--hard-color-cyan); } .weaknesses span { color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
.history { padding: var(--hard-space-4); border-radius: var(--hard-radius-sm); background: var(--hard-color-surface-raised); } .history header { display: flex; justify-content: space-between; gap: var(--hard-space-3); } pre { max-width: 100%; margin: 0; padding: var(--hard-space-3); overflow: auto; border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-space); white-space: pre-wrap; overflow-wrap: anywhere; } .empty-state, .notice { margin: 0; color: var(--hard-color-muted); } .notice { padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); color: var(--hard-color-danger); background: color-mix(in srgb, var(--hard-color-danger) 12%, transparent); }
@media (max-width: 48rem) { .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } .history header, .mastery li, .weaknesses li { align-items: start; flex-direction: column; } }
</style>
