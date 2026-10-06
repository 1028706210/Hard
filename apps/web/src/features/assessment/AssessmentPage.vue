<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import CodeExercise from "./CodeExercise.vue";
import KnowledgeQuestion from "./KnowledgeQuestion.vue";
import { assessmentStore } from "./assessment.store";

const route = useRoute();
const selectedIndex = ref(0);
const lessonId = () => String(route.params.lessonId ?? "");
const selected = computed(() => assessmentStore.state.lesson?.exercises[selectedIndex.value] ?? null);
const running = computed(() => assessmentStore.state.run?.status === "queued" || assessmentStore.state.run?.status === "running");
async function load() { await assessmentStore.loadLesson(lessonId()).catch(() => undefined); selectedIndex.value = 0; }
async function submitKnowledge(answer: string, hintLevel: string) { if (selected.value) await assessmentStore.submitKnowledge(selected.value, answer, hintLevel).catch(() => undefined); }
async function runCode(source: string) { if (selected.value) await assessmentStore.runCode(selected.value, source).catch(() => undefined); }
async function cancel() { if (assessmentStore.state.runningJobId) await assessmentStore.cancelRun(assessmentStore.state.runningJobId).catch(() => undefined); }
onMounted(load);
watch(() => route.params.lessonId, load);
</script>

<template>
  <section class="assessment-page">
    <header><p>可信运行与评分</p><h1>练习工作区</h1></header>
    <div v-if="assessmentStore.state.lesson" class="assessment-page__layout">
      <nav aria-label="课时练习"><button v-for="(exercise, index) in assessmentStore.state.lesson.exercises" :key="exercise.id" type="button" :aria-pressed="index === selectedIndex" @click="selectedIndex = index">{{ exercise.type === "knowledge" ? "知识题" : exercise.type === "code" ? "代码题" : "挑战" }}</button></nav>
      <main v-if="selected" class="assessment-page__card">
        <KnowledgeQuestion v-if="selected.type === 'knowledge' || selected.type === 'scenario'" :exercise="selected" @submit="submitKnowledge" />
        <CodeExercise v-else :exercise="selected" :result="assessmentStore.state.run" :running="running" @run="runCode" @cancel="cancel" />
        <p v-if="assessmentStore.state.assessment" class="assessment-page__score">本题得分：{{ assessmentStore.state.assessment.question_score }}</p>
      </main>
    </div>
    <p v-else>正在读取练习。</p>
  </section>
</template>

<style scoped>
.assessment-page { display: grid; gap: var(--hard-space-5); max-width: 90rem; margin: 0 auto; }
header p { margin: 0; color: var(--hard-color-primary-strong); } h1 { margin: var(--hard-space-1) 0 0; font-size: clamp(2rem, 5vw, 3.5rem); }
.assessment-page__layout { display: grid; grid-template-columns: minmax(10rem, 14rem) minmax(0, 1fr); gap: var(--hard-space-4); }
nav { display: grid; align-content: start; gap: var(--hard-space-2); } nav button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-surface-raised); font: inherit; text-align: left; cursor: pointer; } nav button[aria-pressed="true"] { background: var(--hard-color-primary); }
.assessment-page__card { min-width: 0; padding: var(--hard-space-5); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
.assessment-page__score { margin: var(--hard-space-4) 0 0; color: var(--hard-color-cyan); font-weight: 700; }
@media (max-width: 52rem) { .assessment-page__layout { grid-template-columns: 1fr; } nav { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
