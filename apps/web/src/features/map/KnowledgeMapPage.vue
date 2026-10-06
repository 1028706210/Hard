<script setup lang="ts">
import MobileRouteMap from "./MobileRouteMap.vue";
import OrbitalMap from "./OrbitalMap.vue";
import { onMounted } from "vue";
import { refreshMapSnapshot, useMapStore } from "./map.store";

const snapshot = useMapStore();
onMounted(() => { void refreshMapSnapshot(); });
</script>

<template>
  <section class="knowledge-map" aria-labelledby="knowledge-map-title">
    <header class="knowledge-map__header">
      <div>
        <p class="knowledge-map__eyebrow">Hard · 自适应学习路线</p>
        <h1 id="knowledge-map-title">知识星图<span class="visually-hidden">主页</span></h1>
      </div>
      <dl class="learning-metrics" aria-label="学习概览">
        <div><dt>今日目标</dt><dd>{{ snapshot.dailyGoal }}</dd></div>
        <div><dt>等级</dt><dd>{{ snapshot.level }}</dd></div>
        <div><dt>连续学习</dt><dd>{{ snapshot.streakDays }}</dd></div>
        <div><dt>待复习</dt><dd>{{ snapshot.dueReviews }}</dd></div>
        <div><dt>掌握度</dt><dd>{{ snapshot.mastery }}</dd></div>
      </dl>
    </header>
    <OrbitalMap :snapshot="snapshot" />
    <MobileRouteMap :snapshot="snapshot" />
  </section>
</template>

<style scoped>
.knowledge-map { display: grid; gap: var(--hard-space-5); max-width: 90rem; margin: 0 auto; }
.knowledge-map__header { display: flex; align-items: end; justify-content: space-between; gap: var(--hard-space-5); }
.knowledge-map__eyebrow { margin: 0 0 var(--hard-space-1); color: var(--hard-color-primary-strong); font-size: var(--hard-text-sm); }
h1 { margin: 0; font-size: clamp(2rem, 5vw, 4.25rem); letter-spacing: 0.02em; }
.visually-hidden { position: absolute; width: 0.0625rem; height: 0.0625rem; padding: 0; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
.learning-metrics { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: var(--hard-space-2); margin: 0; }
.learning-metrics div { min-width: 6.75rem; padding: var(--hard-space-2) var(--hard-space-3); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); background: var(--hard-color-surface); }
dt { color: var(--hard-color-muted); font-size: var(--hard-text-xs); }
dd { margin: var(--hard-space-1) 0 0; color: var(--hard-color-text); font-size: var(--hard-text-sm); font-weight: 700; }

@media (max-width: 52rem) {
  .knowledge-map__header { align-items: start; flex-direction: column; }
  .learning-metrics { justify-content: flex-start; }
  .learning-metrics div { min-width: 5.75rem; }
  :deep(.orbital-map) { display: none; }
}
</style>
