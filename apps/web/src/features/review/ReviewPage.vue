<script setup lang="ts">
import { onMounted, ref } from "vue";

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
const keys = new Map<number, string>();

function keyFor(id: number) {
  const existing = keys.get(id);
  if (existing) return existing;
  const value = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${id}`;
  keys.set(id, value);
  return value;
}

async function load() {
  try {
    const [review, weakness] = await Promise.all([
      requestJson<{ items: ReviewItem[] }>("/api/review/queue"),
      requestJson<{ items: Weakness[] }>("/api/growth/weaknesses"),
    ]);
    queue.value = Array.isArray(review.items) ? review.items : [];
    weaknesses.value = Array.isArray(weakness.items) ? weakness.items : [];
  } catch {
    error.value = "暂时无法读取复习数据。";
  }
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
    <header><p>以固定间隔巩固掌握度</p><h1 id="review-title">复习中心</h1></header>
    <p v-if="error" class="notice notice--error" role="alert">{{ error }}</p>
    <p v-if="message" class="notice notice--success" role="status">{{ message }}</p>
    <section class="panel" data-review-queue="true" aria-labelledby="scheduled-review-title">
      <div class="panel__heading"><div><p class="eyebrow">Scheduled review</p><h2 id="scheduled-review-title">计划复习</h2></div><span>{{ queue.length }} 项待处理</span></div>
      <p v-if="!queue.length" class="empty-state">当前没有到期复习。普通错题不会被混入此队列。</p>
      <ul v-else class="review-list">
        <li v-for="item in queue" :key="item.id">
          <div><strong>{{ item.concept_id }}</strong><span>到期 {{ item.due_on }} · 间隔 {{ item.interval_days }} 天</span></div>
          <div class="score-actions"><button :data-review-score="80" type="button" @click="score(item, 80)">掌握（80）</button><button type="button" @click="score(item, 50)">仍需练习（50）</button></div>
        </li>
      </ul>
    </section>
    <section class="panel" data-wrong-answer-browser="true" aria-labelledby="wrong-answer-title">
      <div class="panel__heading"><div><p class="eyebrow">Signals, not a review schedule</p><h2 id="wrong-answer-title">普通错题浏览</h2></div><span>{{ weaknesses.length }} 个弱点线索</span></div>
      <p v-if="!weaknesses.length" class="empty-state">还没有普通错题线索。</p>
      <ul v-else class="wrong-list"><li v-for="item in weaknesses" :key="`${item.concept_id}-${item.exercise_id}`"><a :href="`/assessment/${item.lesson_id}`">{{ item.concept_id }}</a><span>近期弱点分 {{ item.score }} · {{ item.exercise_id }}</span></li></ul>
    </section>
  </section>
</template>

<style scoped>
.review-page { display: grid; gap: var(--hard-space-5); max-width: 70rem; margin: 0 auto; }
header p, .eyebrow { margin: 0; color: var(--hard-color-primary-strong); font-size: var(--hard-text-sm); } h1, h2 { margin: var(--hard-space-1) 0 0; } h1 { font-size: clamp(2rem, 5vw, 3.5rem); } h2 { font-size: var(--hard-text-xl); }
.panel { padding: var(--hard-space-5); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); } .panel__heading { display: flex; align-items: start; justify-content: space-between; gap: var(--hard-space-3); } .panel__heading > span { color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
.review-list, .wrong-list { display: grid; gap: var(--hard-space-2); padding: 0; margin: var(--hard-space-4) 0 0; list-style: none; } .review-list li, .wrong-list li { display: flex; align-items: center; justify-content: space-between; gap: var(--hard-space-4); padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); background: var(--hard-color-surface-raised); } strong, a { color: var(--hard-color-cyan); } .review-list span, .wrong-list span { display: block; margin-top: var(--hard-space-1); color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
.score-actions { display: flex; flex-wrap: wrap; gap: var(--hard-space-2); } button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: transparent; font: inherit; cursor: pointer; } button:first-child { border-color: var(--hard-color-primary); background: var(--hard-color-primary); }
.empty-state { margin: var(--hard-space-4) 0 0; color: var(--hard-color-muted); } .notice { margin: 0; padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); } .notice--success { color: var(--hard-color-cyan); background: color-mix(in srgb, var(--hard-color-cyan) 12%, transparent); } .notice--error { color: var(--hard-color-danger); background: color-mix(in srgb, var(--hard-color-danger) 12%, transparent); }
@media (max-width: 42rem) { .panel { padding: var(--hard-space-4); } .review-list li, .wrong-list li { align-items: start; flex-direction: column; } .score-actions { width: 100%; } .score-actions button { flex: 1; } }
</style>
