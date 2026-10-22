<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import { requestJson, type GrowthSummaryResponse } from "../../api/client";
import { chainLabels, type ChainCourse, type ChainConcept } from "../map/constellation";

interface Summary extends GrowthSummaryResponse { total_experience: number; level: number; current_level_progress: number; next_level_remaining: number; streak_days: number; badges: string[]; mastery: Array<{ scope_type: string; scope_id: string; score: number }>; }
interface HistoryItem { id: string; exercise_id: string; language: string | null; source_code: string; normalized_result: Record<string, unknown>; score: number; duration_ms: number | null; created_at: string; diff: string; }
interface Weakness { concept_id: string; score: number; lesson_id: string; exercise_id: string; }
interface ActivityDay { date: string; time_spent_seconds: number; completed_exercises: number; }

const summary = ref<Summary | null>(null);
const history = ref<HistoryItem[]>([]);
const weaknesses = ref<Weakness[]>([]);
const error = ref("");
const names = ref<Record<string, string>>({});
const masteryScope = ref("");
const masteryLanguage = ref("");
const masterySearch = ref("");
const masteryLimit = ref(12);
const filteredMastery = computed(() => (summary.value?.mastery ?? []).filter(item => {
  const query = masterySearch.value.trim().toLowerCase();
  return (!masteryScope.value || item.scope_type === masteryScope.value)
    && (!masteryLanguage.value || item.scope_id === masteryLanguage.value || item.scope_id.startsWith(`${masteryLanguage.value}-`))
    && (!query || `${item.scope_id} ${displayName(item.scope_id)}`.toLowerCase().includes(query));
}));
const visibleMastery = computed(() => filteredMastery.value.slice(0, masteryLimit.value));
watch([masteryScope, masteryLanguage, masterySearch], () => { masteryLimit.value = 12; });
function resetMastery() { masteryScope.value = ""; masteryLanguage.value = ""; masterySearch.value = ""; masteryLimit.value = 12; }
const badgeLabels: Record<string, string> = { first_lesson: "完成第一课", first_module_mastery: "掌握第一个模块", seven_day_streak: "连续学习七天" };
const activityCells = computed(() => {
  const growth = summary.value;
  if (!growth || !Array.isArray(growth.activity_days) || typeof growth.activity_start_date !== "string") return [];
  const start = new Date(`${growth.activity_start_date}T00:00:00Z`).getTime();
  if (!Number.isFinite(start)) return [];
  const activity = new Map((growth.activity_days as ActivityDay[]).map(day => [day.date, day]));
  return Array.from({ length: 90 }, (_, index) => {
    const date = new Date(start + index * 86400000).toISOString().slice(0, 10);
    const day = activity.get(date);
    return { date, level: day ? Math.min(4, Math.max(1, day.completed_exercises)) : 0,
      description: day ? `${date}：${day.completed_exercises} 道已完成练习，记录学习时间 ${day.time_spent_seconds} 秒` : `${date}：暂无学习记录` };
  });
});
function displayName(id: string) { return names.value[id] ?? id; }
function exerciseName(id: string) {
  const match = /^(.*)-((?:c|k|ch)\d+)$/.exec(id);
  return match && names.value[match[1]] ? `${names.value[match[1]]} · ${match[2]}` : displayName(id);
}
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

async function loadNames() {
  const [catalog, comparison] = await Promise.allSettled([
    requestJson<{ courses: ChainCourse[] }>("/api/content/catalog"),
    requestJson<{ concepts: ChainConcept[] }>("/api/compare/concepts"),
  ]);
  const labels: Record<string, string> = {};
  if (catalog.status === "fulfilled") for (const course of catalog.value.courses) {
    labels[course.language] = chainLabels[course.language];
    for (const module of course.modules) {
      labels[module.id] = module.title;
      for (const lesson of module.lessons) labels[lesson.id] = lesson.title;
    }
  }
  if (comparison.status === "fulfilled") for (const concept of comparison.value.concepts) labels[concept.id] = concept.name;
  names.value = labels;
}
onMounted(() => { void load(); void loadNames(); });
</script>

<template>
  <section class="growth-page" aria-labelledby="growth-title">
    <header><p>每一次练习，都有迹可循</p><h1 id="growth-title">成长报告</h1><p class="page-intro">从真实记录中，看见积累，也找到下一步。</p></header>
    <p v-if="error" class="notice" role="alert">{{ error }}</p>
    <template v-else-if="summary">
      <section class="metrics" aria-label="成长概览"><div><span>经验</span><strong>{{ summary.total_experience }} XP</strong></div><div><span>等级</span><strong>{{ summary.level }}</strong></div><div><span>连续学习</span><strong>{{ summary.streak_days }} 天</strong></div><div><span>下级还需</span><strong>{{ summary.next_level_remaining }} XP</strong></div></section>
      <section class="panel badge-panel"><div class="section-heading"><h2>学习徽章</h2><span>里程碑</span></div><p v-if="!summary.badges.length" class="empty-state">尚未获得徽章。完成第一课，留下你的第一个里程碑。</p><ul v-else class="badges"><li v-for="badge in summary.badges" :key="badge"><span aria-hidden="true">✧</span> {{ badgeLabels[badge] ?? badge }}</li></ul></section>
      <section class="panel"><h2>学习热力图</h2><template v-if="activityCells.length"><p class="empty-state">最近 90 天的真实学习记录，颜色随当天已完成练习数加深。日期以服务端记录为准。</p><div class="activity-grid" aria-label="最近90天学习活动"><span v-for="cell in activityCells" :key="cell.date" role="img" :aria-label="cell.description" :title="cell.description" :data-activity-date="cell.date" :data-level="cell.level"></span></div><div class="activity-caption"><span>{{ summary.activity_start_date }}</span><span>无记录 → 访问或1题 → 2 / 3 / 4+</span><span>{{ summary.activity_end_date }}</span></div></template><p v-else class="empty-state">热力图数据尚不可用。完成练习后，可在掌握度与提交历史中查看自己的进步。</p></section>
      <section class="panel" aria-labelledby="mastery-title">
        <div class="section-heading"><div><h2 id="mastery-title">知识掌握度</h2><p class="section-description">按课程、模块或课时，查看每一份练习的积累。</p></div><span>{{ summary.mastery.length }} 条记录</span></div>
        <p v-if="!summary.mastery.length" class="empty-state">尚无掌握度记录。完成练习后，这里会显示真实得分。</p>
        <template v-else>
          <div class="mastery-filters"><label>学习范围<select v-model="masteryScope" data-mastery-scope><option value="">全部范围</option><option value="course">课程</option><option value="module">模块</option><option value="lesson">课时</option></select></label><label>学习语言<select v-model="masteryLanguage" data-mastery-language><option value="">全部语言</option><option value="python">Python</option><option value="java">Java</option><option value="csharp">C#</option><option value="cpp">C++</option></select></label><label class="mastery-query">查找记录<input v-model="masterySearch" data-mastery-search type="search" placeholder="输入名称或 ID"></label></div>
          <div class="mastery-status"><span role="status">显示 {{ visibleMastery.length }} / {{ filteredMastery.length }} 条记录</span><button v-if="masteryScope || masteryLanguage || masterySearch" data-reset-mastery type="button" @click="resetMastery">清除筛选</button></div>
          <p v-if="!filteredMastery.length" class="empty-state">没有匹配的掌握度记录，请调整筛选条件。</p>
          <ul v-else class="mastery"><li v-for="item in visibleMastery" :key="`${item.scope_type}-${item.scope_id}`" data-mastery-record :data-scope-id="item.scope_id"><span>{{ scopeLabel(item.scope_type) }} · {{ displayName(item.scope_id) }}</span><strong>{{ item.score }}%</strong><meter :value="item.score" min="0" max="100" :aria-label="`${scopeLabel(item.scope_type)} ${displayName(item.scope_id)} 掌握度`">{{ item.score }}%</meter></li></ul>
          <button v-if="visibleMastery.length < filteredMastery.length" class="more-button" data-more-mastery type="button" @click="masteryLimit += 12">继续查看 · 还有 {{ filteredMastery.length - visibleMastery.length }} 条</button>
        </template>
      </section>
      <section class="panel"><h2>弱点链接</h2><p v-if="!weaknesses.length" class="empty-state">没有近期弱点。</p><ul v-else class="weaknesses"><li v-for="item in weaknesses" :key="`${item.concept_id}-${item.exercise_id}`"><a data-weakness-link :href="`/assessment/${item.lesson_id}`">{{ displayName(item.concept_id) }}</a><span>分数 {{ item.score }} · {{ exerciseName(item.exercise_id) }}</span></li></ul></section>
      <section class="panel"><h2>代码成长历史</h2><p v-if="!history.length" class="empty-state">尚无代码提交历史。</p><article v-for="item in history" v-else :key="item.id" class="history"><header><strong>{{ exerciseName(item.exercise_id) }}</strong><span>{{ item.language ?? "未知语言" }} · {{ item.score }} 分 · {{ item.created_at }}</span></header><h3>源码</h3><pre data-plain-text="source">{{ item.source_code }}</pre><h3>与上一份提交的差异</h3><pre data-plain-text="diff">{{ item.diff }}</pre></article></section>
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
.mastery li { display: grid; grid-template-columns: minmax(0,1fr) auto; } .mastery li > span { overflow-wrap: anywhere; } .mastery meter { grid-column: 1 / -1; width: 100%; height: .75rem; accent-color: var(--hard-color-cyan); } .mastery meter::-webkit-meter-bar { background: var(--hard-color-space); border: 0; } .mastery meter::-webkit-meter-optimum-value { background: linear-gradient(90deg, var(--hard-color-primary), var(--hard-color-cyan)); }
.metrics { gap: 0; padding-block: 1.5rem; border-block: 1px solid var(--hard-color-line); }
.metrics div { padding: .5rem 1.5rem; border: 0; border-right: 1px solid var(--hard-color-line); border-radius: 0; background: transparent; }
.metrics div:first-child { padding-left: 0; }
.metrics div:last-child { border-right: 0; }
.metrics strong { font-size: 1.75rem; font-weight: 500; color: var(--hard-color-text); font-variant-numeric: tabular-nums; }
.panel { padding: 1.5rem; gap: 1.25rem; }
.empty-state { line-height: 1.8; }
.history { border: 1px solid var(--hard-color-line); background: transparent; }
.history header { flex-wrap: wrap; overflow-wrap: anywhere; }
@media (max-width: 48rem) { .metrics { row-gap: 1.5rem; } .metrics div:nth-child(odd) { padding-left: 0; } .metrics div:nth-child(even) { border-right: 0; } .panel { padding: 1.25rem; } }
.activity-grid { display: grid; grid-template-rows: repeat(7, 1fr); grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); gap: .3rem; max-width: 38rem; }
.activity-grid span { aspect-ratio: 1; max-height: 1.8rem; border: 1px solid var(--hard-color-line); border-radius: .2rem; background: var(--hard-color-space); }
.activity-grid [data-level="1"] { background: color-mix(in srgb, var(--hard-color-cyan) 22%, var(--hard-color-space)); }
.activity-grid [data-level="2"] { background: color-mix(in srgb, var(--hard-color-cyan) 42%, var(--hard-color-space)); }
.activity-grid [data-level="3"] { background: color-mix(in srgb, var(--hard-color-cyan) 65%, var(--hard-color-space)); }
.activity-grid [data-level="4"] { background: var(--hard-color-cyan); }
.activity-caption { display: flex; flex-wrap: wrap; justify-content: space-between; gap: .5rem; color: var(--hard-color-muted); font-size: .75rem; }
.page-intro { margin-top: .85rem; color: var(--hard-color-muted); line-height: 1.8; }
.section-heading { display: flex; justify-content: space-between; align-items: start; gap: 1rem; }
.section-heading > span, .section-description { margin: .5rem 0 0; color: var(--hard-color-muted); font-size: .875rem; line-height: 1.7; }
.badge-panel { border-style: dashed; background: transparent; }
.badges li { color: var(--hard-color-amber); border: 1px solid color-mix(in srgb, var(--hard-color-amber) 25%, transparent); }
.mastery { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .75rem 1.25rem; }
.mastery li { padding: 1rem 0; border-bottom: 1px solid var(--hard-color-line); border-radius: 0; background: transparent; font-size: .875rem; }
.mastery strong { color: var(--hard-color-cyan); font-variant-numeric: tabular-nums; }
.mastery-filters { display: grid; grid-template-columns: 1fr 1fr 2fr; gap: .75rem; }
.mastery-filters label { display: grid; gap: .5rem; color: var(--hard-color-muted); font-size: .8rem; }
.mastery-filters select, .mastery-filters input { width: 100%; min-width: 0; min-height: var(--hard-touch-target); padding: .5rem .75rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-space); font: inherit; }
.mastery-status { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: .5rem; color: var(--hard-color-muted); font-size: .8rem; }
.mastery-status button, .more-button { min-height: var(--hard-touch-target); padding: .5rem 1rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-cyan); background: transparent; font: inherit; cursor: pointer; }
.more-button { justify-self: center; }
.activity-grid { max-width: 42rem; }
@media (max-width: 42rem) { .mastery { grid-template-columns: 1fr; } .mastery-filters { grid-template-columns: 1fr 1fr; } .mastery-query { grid-column: 1 / -1; } .section-heading { flex-wrap: wrap; } }
</style>
