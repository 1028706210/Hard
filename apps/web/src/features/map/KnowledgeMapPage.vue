<script setup lang="ts">
import ConstellationPage from "./ConstellationPage.vue";
import { nextTick, onMounted, ref, watch } from "vue";
import { refreshMapSnapshot, useMapStore } from "./map.store";

const snapshot = useMapStore();
const feedback = ref<HTMLElement>();
onMounted(() => { void refreshMapSnapshot(); });
watch(() => snapshot.loadState, async (state) => {
  if (state === "error") { await nextTick(); feedback.value?.focus(); }
});
</script>

<template>
  <section class="knowledge-map" aria-labelledby="knowledge-map-title">
    <header class="knowledge-map__header">
      <div class="home-intro"><p class="knowledge-map__eyebrow">YOUR LEARNING UNIVERSE</p><h1 id="knowledge-map-title" aria-label="知识星图主页">知识星图</h1><p class="home-subtitle">连接知识的脉络，找到下一步的方向。</p></div>
      <RouterLink v-if="snapshot.loadState === 'ready' && snapshot.continueLessonId" class="home-continue" :to="`/lesson/${snapshot.continueLessonId}`" data-continue-learning><span class="continue-kicker">继续学习</span><strong>{{ snapshot.continueLessonTitle }}</strong><span class="continue-arrow" aria-hidden="true">→</span><small>从上次停下的地方，继续探索</small></RouterLink>
    </header>
    <div v-if="snapshot.loadState === 'error'" ref="feedback" class="knowledge-map__feedback" role="alert" tabindex="-1"><p>{{ snapshot.error }}</p><button type="button" @click="refreshMapSnapshot()">重试读取学习概览</button></div>
    <p v-else-if="snapshot.loadState === 'loading'" class="knowledge-map__feedback" role="status">正在读取学习概览。</p>
    <template v-else>
      <dl class="learning-metrics" aria-label="学习概览">
        <div><dt>今日目标</dt><dd>{{ snapshot.dailyGoal }}</dd></div><div><dt>学习等级</dt><dd>{{ snapshot.level }}</dd></div><div><dt>连续学习</dt><dd>{{ snapshot.streakDays }}</dd></div><div><dt>待复习</dt><dd>{{ snapshot.dueReviews }}</dd></div><div title="全部课时最高测评分的平均值；未测评课时按 0 计"><dt>全课程掌握度</dt><dd>{{ snapshot.mastery }}</dd></div>
      </dl>
      <ConstellationPage home />
    </template>
  </section>
</template>
<style scoped>
.knowledge-map { max-width:1320px;margin:0 auto;display:grid;gap:1rem; }
.knowledge-map__header { display:flex;justify-content:space-between;align-items:center;gap:2rem;padding:0; }
.knowledge-map__eyebrow { margin:0 0 .85rem;color:#a1b1d5;font:500 .68rem "Segoe UI",sans-serif;letter-spacing:.22em; }
h1 { margin:0;font-size:clamp(2.2rem,3.5vw,3.1rem);line-height:1.2;font-weight:550;letter-spacing:.025em; }
.home-subtitle { margin:1rem 0 0;color:#9ba8b9;font-size:.94rem;letter-spacing:.05em; }
.home-continue { display:grid;grid-template-columns:1fr auto;gap:.5rem 1.75rem;min-width:295px;max-width:430px;padding:1.1rem 1.5rem;border:1px solid #65789b80;border-radius:12px;background:#1b293e;color:#eff3ff;text-decoration:none;box-shadow:0 8px 28px #00000015; }
.home-continue:hover { background:#1c2b43;border-color:#aebcf7; }
.continue-kicker { grid-column:1;font-size:.72rem;color:#aebcf7;letter-spacing:.1em; }
.home-continue strong { font-size:1.03rem;font-weight:550; }
.continue-arrow { grid-column:2;grid-row:1/4;align-self:center;font-size:1.5rem;color:#cbd6fa; }
.home-continue small { color:#96a6c0;font-size:.72rem; }
.learning-metrics { display:grid;grid-template-columns:1.25fr repeat(4,1fr);margin:0;padding:1rem 0;border-top:1px solid #ffffff10;border-bottom:1px solid #ffffff10; }
.learning-metrics div { padding:0 1.75rem;border-left:1px solid #ffffff10; }
.learning-metrics div:first-child {padding-left:0;border:0;}
dt {font-size:.72rem;color:#a4b2c7;letter-spacing:.05em;}
dd {margin:.4rem 0 0;font:500 1.35rem "Bahnschrift","Segoe UI",sans-serif;color:#e5eaf3;}
.knowledge-map__feedback {padding:2rem;border:1px solid var(--hard-color-line);border-radius:12px;background:var(--hard-color-surface);}
.knowledge-map__feedback button {padding:.8rem 1.2rem;border:0;border-radius:8px;color:white;background:var(--hard-color-primary);}
@media(max-width:52rem) { .knowledge-map {gap:1.5rem;} .knowledge-map__header {align-items:stretch;flex-direction:column;gap:1.5rem;padding-top:.5rem;} .home-continue {min-width:0;max-width:none;} .learning-metrics {grid-template-columns:repeat(3,1fr);gap:1.2rem 0;} .learning-metrics div {padding:0 1rem;} .learning-metrics div:nth-child(4) {padding-left:0;border:0;} dd {font-size:1.1rem;} }
@media(max-width:30rem) { .home-subtitle {font-size:.83rem;} .learning-metrics div {padding-inline:.65rem;} dt {font-size:.68rem;} }
</style>
