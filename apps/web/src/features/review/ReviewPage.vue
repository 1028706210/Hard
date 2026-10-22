<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { requestJson } from "../../api/client";

interface ReviewItem {
  id: number;
  concept_id: string;
  lesson_id: string | null;
  exercise_id: string | null;
  due_on: string;
  interval_days: number;
  last_score: number | null;
}
interface Weakness { concept_id: string; score: number; lesson_id: string; exercise_id: string; }

const queue = ref<ReviewItem[]>([]);
const weaknesses = ref<Weakness[]>([]);
const message = ref("");
const error = ref("");
const loading = ref(true);
const keys = new Map<number, string>();

function keyFor(id: number) {
  const existing = keys.get(id);
  if (existing) return existing;
  const value = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${id}`;
  keys.set(id, value);
  return value;
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [review, weakness] = await Promise.all([
      requestJson<{ items: ReviewItem[] }>("/api/review/queue"),
      requestJson<{ items: Weakness[] }>("/api/growth/weaknesses"),
    ]);
    queue.value = Array.isArray(review.items) ? review.items : [];
    weaknesses.value = Array.isArray(weakness.items) ? weakness.items : [];
  } catch {
    error.value = "暂时无法读取复习数据。";
  } finally { loading.value = false; }
}

async function score(item: ReviewItem, value: number) {
  try {
    const result = await requestJson<{ due_on: string }>(`/api/review/items/${item.id}`, {
      method: "POST",
      headers: { "content-type": "application/json", "Idempotency-Key": keyFor(item.id) },
      body: JSON.stringify({ score: value }),
    });
    message.value = `下次复习：${result.due_on}`;
    await load();
  } catch {
    error.value = "复习评分尚未保存，请重试。";
  }
}

onMounted(load);
</script>

<template>
  <section class="review-page" aria-labelledby="review-title">
    <header><p>温故知新，让每一次练习留下收获</p><h1 id="review-title">复习中心</h1><p class="page-intro">按计划回顾已学知识，或回到练习中巩固薄弱之处。</p></header>
    <p v-if="error" class="notice notice--error" role="alert">{{ error }}</p>
    <p v-if="message" class="notice notice--success" role="status">{{ message }}</p>
    <section class="panel" data-review-queue="true" aria-labelledby="scheduled-review-title">
      <div class="panel__heading"><div><p class="eyebrow">01 · 按计划回顾</p><h2 id="scheduled-review-title">计划复习</h2></div><span v-if="!loading && !error" class="queue-count">{{ queue.length }} 项待处理</span></div>
      <p v-if="loading" class="empty-state" role="status">正在读取复习数据…</p>
      <p v-else-if="error" class="empty-state">复习清单暂时不可用，请稍后重试。</p>
      <div v-else-if="!queue.length" class="review-empty"><span class="empty-symbol" aria-hidden="true">○</span><div><h3>当前没有到期复习</h3><p class="empty-state">复习计划会在到期时出现在这里。现在可以继续学习，或回看下面的薄弱知识。</p><RouterLink to="/course/python">继续学习课程 <span aria-hidden="true">↗</span></RouterLink></div></div>
      <ul v-else class="review-list">
        <li v-for="item in queue" :key="item.id" :data-review-item-id="item.id">
          <div><strong>{{ item.concept_id }}</strong><span>到期 {{ item.due_on }} · 间隔 {{ item.interval_days }} 天</span><a v-if="item.lesson_id" class="review-lesson" :href="`/lesson/${item.lesson_id}`">回看课时 →</a></div>
          <div class="score-actions"><button :data-review-score="80" type="button" @click="score(item, 80)">掌握（80）</button><button type="button" @click="score(item, 50)">仍需练习（50）</button></div>
        </li>
      </ul>
    </section>
    <section class="panel" data-wrong-answer-browser="true" aria-labelledby="wrong-answer-title">
      <div class="panel__heading"><div><p class="eyebrow">02 · 主动巩固</p><h2 id="wrong-answer-title">普通错题浏览</h2></div><span v-if="!loading && !error">{{ weaknesses.length }} 个弱点线索</span></div>
      <p class="section-description">回到对应练习重新尝试。这些薄弱线索与到期复习分别展示。</p>
      <p v-if="loading" class="empty-state">正在读取练习线索…</p><p v-else-if="error" class="empty-state">练习线索暂时不可用。</p>
      <div v-else-if="!weaknesses.length" class="practice-empty"><p class="empty-state">还没有普通错题线索。</p><span>完成练习后，在这里回看需要巩固的知识。</span></div>
      <ul v-else class="wrong-list"><li v-for="item in weaknesses" :key="`${item.concept_id}-${item.exercise_id}`"><a :href="`/assessment/${item.lesson_id}`">{{ item.concept_id }}</a><span>近期弱点分 {{ item.score }} · {{ item.exercise_id }}</span></li></ul>
    </section>
    <RouterLink v-if="!loading && !error" class="star-chain-entry" to="/constellations"><span>给已学知识建立新联系</span><small>去星链中探索相似概念 →</small></RouterLink>
  </section>
</template>

<style scoped>
.review-page { display: grid; gap: var(--hard-space-5); max-width: 70rem; margin: 0 auto; }
header p, .eyebrow { margin: 0; color: var(--hard-color-primary-strong); font-size: var(--hard-text-sm); } h1, h2 { margin: var(--hard-space-1) 0 0; } h1 { font-size: clamp(2rem, 5vw, 3.5rem); } h2 { font-size: var(--hard-text-xl); }
.panel { padding: var(--hard-space-5); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); } .panel__heading { display: flex; align-items: start; justify-content: space-between; gap: var(--hard-space-3); } .panel__heading > span { color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
.review-list, .wrong-list { display: grid; gap: var(--hard-space-2); padding: 0; margin: var(--hard-space-4) 0 0; list-style: none; } .review-list li, .wrong-list li { display: flex; align-items: center; justify-content: space-between; gap: var(--hard-space-4); padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); background: var(--hard-color-surface-raised); } strong, a { color: var(--hard-color-cyan); } .review-list span, .wrong-list span { display: block; margin-top: var(--hard-space-1); color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
.score-actions { display: flex; flex-wrap: wrap; gap: var(--hard-space-2); } button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: transparent; font: inherit; cursor: pointer; } button:first-child { border-color: var(--hard-color-primary); background: var(--hard-color-primary); }
.empty-state { margin: var(--hard-space-4) 0 0; color: var(--hard-color-muted); } .notice { margin: 0; padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); } .notice--success { color: var(--hard-color-cyan); background: color-mix(in srgb, var(--hard-color-cyan) 12%, transparent); } .notice--error { color: var(--hard-color-danger); background: color-mix(in srgb, var(--hard-color-danger) 12%, transparent); }
.review-empty { display: flex; align-items: start; gap: 1.5rem; padding: 2rem 0 .5rem; }
.empty-symbol { display: grid; place-items: center; flex: 0 0 44px; height: 44px; border: 1px solid var(--hard-color-line); border-radius: 50%; color: var(--hard-color-cyan); }
.review-empty h3 { margin: 0; font-size: 1.125rem; font-weight: 600; }
.review-empty p { margin: .75rem 0 1.25rem; line-height: 1.8; }
.review-empty a { display: inline-flex; align-items: center; gap: 1rem; min-height: 44px; font-size: .875rem; }
.practice-empty { padding: .5rem 0; }
.practice-empty > span { display: block; margin-top: .5rem; color: var(--hard-color-muted); line-height: 1.8; font-size: .875rem; }
@media (max-width: 42rem) { .panel { padding: var(--hard-space-4); } .review-list li, .wrong-list li { align-items: start; flex-direction: column; } .score-actions { width: 100%; } .score-actions button { flex: 1; } }
.page-intro { margin-top: .85rem; color: var(--hard-color-muted); line-height: 1.8; }
.panel[data-review-queue] { border-top: 2px solid color-mix(in srgb, var(--hard-color-cyan) 45%, var(--hard-color-line)); }
.panel__heading { align-items: center; }
.panel__heading .queue-count { padding: .5rem .85rem; border: 1px solid var(--hard-color-line); border-radius: 999px; color: var(--hard-color-cyan); white-space: nowrap; }
.review-empty { padding: 1.75rem 0 .25rem; }
.empty-symbol { color: var(--hard-color-primary-strong); background: color-mix(in srgb, var(--hard-color-primary) 8%, transparent); }
.review-list li, .wrong-list li { padding: 1.25rem 0; border-bottom: 1px solid var(--hard-color-line); border-radius: 0; background: transparent; }
.review-lesson { display: inline-flex; align-items: center; min-height: var(--hard-touch-target); font-size: .8rem; }
.section-description { margin: 1rem 0 0; color: var(--hard-color-muted); line-height: 1.8; font-size: .875rem; }
.practice-empty { padding: 0 0 .25rem; }
.star-chain-entry { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; padding: 1.25rem 1.5rem; border: 1px dashed var(--hard-color-line); border-radius: var(--hard-radius-md); text-decoration: none; }
.star-chain-entry small { color: var(--hard-color-muted); }
@media (max-width: 35rem) { .panel__heading { align-items: start; flex-direction: column; } .review-empty { gap: 1rem; } }
</style>
