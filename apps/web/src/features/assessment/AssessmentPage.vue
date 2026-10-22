<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import CodeExercise from "./CodeExercise.vue";
import KnowledgeQuestion from "./KnowledgeQuestion.vue";
import { assessmentStore } from "./assessment.store";

const route = useRoute();
const selectedIndex = ref(0);
const feedback = ref<HTMLElement>();
const lessonId = () => String(route.params.lessonId ?? "");
const selected = computed(() => assessmentStore.state.lesson?.exercises[selectedIndex.value] ?? null);
const running = computed(() => assessmentStore.state.runState === "running");
async function load() { const lesson = await assessmentStore.loadLesson(lessonId()); if (lesson) selectedIndex.value = 0; }
function selectExercise(index: number) { selectedIndex.value = index; if (selected.value) assessmentStore.selectExercise(selected.value.id); }
async function submitKnowledge(answer: string, hintLevel: string) { if (selected.value) await assessmentStore.submitKnowledge(selected.value, answer, hintLevel); }
async function runCode(source: string) { if (selected.value) await assessmentStore.runCode(selected.value, source); }
async function cancel() { if (assessmentStore.state.runningJobId) await assessmentStore.cancelRun(assessmentStore.state.runningJobId); }
onMounted(load);
watch(() => route.params.lessonId, load);
watch(() => assessmentStore.state.error, async (message) => {
  if (message) { await nextTick(); feedback.value?.focus(); }
});
</script>

<template>
  <section class="assessment-page">
    <header class="assessment-header"><div><p class="assessment-eyebrow">练习 / PRACTICE</p><h1>练习工作区</h1><p class="assessment-description">从理解到独立完成，在实践中巩固每一个概念。</p></div><RouterLink class="back-to-lesson" :to="`/lesson/${lessonId()}`">返回课时 <span aria-hidden="true">↗</span></RouterLink></header>
    <div v-if="assessmentStore.state.loadState === 'error'" ref="feedback" class="assessment-page__feedback" role="alert" tabindex="-1">
      <p>{{ assessmentStore.state.error }}</p>
      <button type="button" @click="load">重新读取练习</button>
    </div>
    <div v-else-if="assessmentStore.state.lesson" class="assessment-page__layout">
      <nav class="exercise-nav" aria-label="课时练习"><p class="exercise-nav__heading">本课练习 <span>{{ assessmentStore.state.lesson.exercises.length }} 题</span></p><button v-for="(exercise, index) in assessmentStore.state.lesson.exercises" :key="exercise.id" type="button" :aria-pressed="index === selectedIndex" @click="selectExercise(index)"><span class="exercise-number" aria-hidden="true">{{ String(index + 1).padStart(2, '0') }}</span><span class="exercise-nav__text"><span>{{ exercise.type === "knowledge" ? "知识题" : exercise.type === "code" ? "代码题" : "挑战" }}</span><small>{{ exercise.prompt }}</small></span></button></nav>
      <div v-if="selected" class="assessment-page__card">
        <div class="exercise-context"><span>{{ selected.type === 'knowledge' ? '理解概念' : selected.type === 'scenario' ? '情境思考' : selected.type === 'code' ? '动手编写' : '综合挑战' }}</span><span>第 {{ selectedIndex + 1 }} / {{ assessmentStore.state.lesson.exercises.length }} 题</span></div>
        <KeepAlive :max="1"><KnowledgeQuestion :key="assessmentStore.state.lesson.id" v-if="selected.type === 'knowledge' || selected.type === 'scenario'" :exercise="selected" @submit="submitKnowledge" /></KeepAlive>
        <CodeExercise v-if="selected.type !== 'knowledge' && selected.type !== 'scenario'" :lesson-id="assessmentStore.state.lesson.id" :language="assessmentStore.state.lesson.language" :exercise="selected" :result="assessmentStore.state.run" :running="running" @run="runCode" @cancel="cancel" />
        <p v-if="assessmentStore.state.assessment" class="assessment-page__score">本题得分：{{ assessmentStore.state.assessment.question_score }}</p>
        <div v-if="assessmentStore.state.error" ref="feedback" class="assessment-page__feedback" role="alert" tabindex="-1"><p>{{ assessmentStore.state.error }}</p></div>
      </div>
      <p v-else class="assessment-page__empty" role="status">本课暂未提供练习，可以先返回课时继续阅读。</p>
    </div>
    <p v-else role="status">正在读取练习。</p>
  </section>
</template>

<style scoped>
.assessment-page { display: grid; gap: 1.75rem; max-width: 84rem; margin: 0 auto; }
.assessment-header { display: flex; justify-content: space-between; align-items: center; gap: 1.25rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--hard-color-line); }
.assessment-eyebrow { margin: 0; color: var(--hard-color-primary-strong); font-size: .7rem; letter-spacing: .08em; }
h1 { margin: .5rem 0 .6rem; font-size: clamp(1.9rem, 3vw, 2.6rem); line-height: 1.35; letter-spacing: -.035em; }
.assessment-description { margin: 0; color: var(--hard-color-muted); font-size: .9rem; line-height: 1.8; }
.back-to-lesson { display: inline-flex; flex-shrink: 0; align-items: center; gap: .75rem; min-height: 44px; padding: .55rem .85rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); text-decoration: none; font-size: .8rem; }
.back-to-lesson:hover { border-color: var(--hard-color-primary-strong); }
.assessment-page__layout { display: grid; grid-template-columns: 14rem minmax(0, 1fr); gap: 1.5rem; align-items: start; }
.exercise-nav { position: sticky; top: 6rem; display: grid; align-content: start; gap: .4rem; min-width: 0; }
.exercise-nav__heading { display: flex; justify-content: space-between; margin: 0 0 .6rem; padding-inline: .8rem; color: var(--hard-color-muted); font-size: .75rem; }
.exercise-nav button { display: flex; align-items: baseline; gap: .7rem; min-width: 0; min-height: 72px; padding: .9rem .8rem; border: 1px solid transparent; border-radius: var(--hard-radius-sm); color: var(--hard-color-muted); background: transparent; font: inherit; text-align: left; cursor: pointer; }
.exercise-nav button:hover { background: var(--hard-color-surface); }
.exercise-nav button[aria-pressed="true"] { border-color: var(--hard-color-line); color: var(--hard-color-text); background: var(--hard-color-surface-raised); box-shadow: inset 2px 0 var(--hard-color-primary-strong); }
.exercise-number { flex-shrink: 0; color: var(--hard-color-primary-strong); font: .7rem ui-monospace, monospace; }
.exercise-nav__text { display: grid; gap: .35rem; min-width: 0; font-size: .85rem; }
.exercise-nav__text small { display: -webkit-box; overflow: hidden; -webkit-line-clamp: 2; -webkit-box-orient: vertical; color: var(--hard-color-muted); font-size: .72rem; line-height: 1.7; }
.assessment-page__card { min-width: 0; padding: clamp(1.25rem, 2.8vw, 2.5rem); border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
.exercise-context { display: flex; justify-content: space-between; flex-wrap: wrap; gap: .75rem; margin-bottom: 1.75rem; padding-bottom: 1rem; border-bottom: 1px solid var(--hard-color-line); color: var(--hard-color-muted); font-size: .75rem; }
.exercise-context span:first-child { color: var(--hard-color-primary-strong); }
.assessment-page__empty { margin: 0; padding: 2rem; color: var(--hard-color-muted); border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-md); }
.assessment-page__feedback { display: grid; gap: var(--hard-space-3); margin-top: var(--hard-space-3); padding: var(--hard-space-3); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); background: var(--hard-color-surface-raised); }
.assessment-page__feedback p { margin: 0; }
.assessment-page__feedback button { min-height: var(--hard-touch-target); width: fit-content; padding: 0 var(--hard-space-3); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; cursor: pointer; }
.assessment-page__score { margin: var(--hard-space-4) 0 0; color: var(--hard-color-cyan); font-weight: 700; }
@media (max-width: 60rem) { .assessment-page__layout { grid-template-columns: 11rem minmax(0, 1fr); gap: 1rem; } }
@media (max-width: 52rem) { .assessment-page { gap: 1.25rem; } .assessment-header { flex-wrap: wrap; padding-bottom: 1rem; } .assessment-page__layout { grid-template-columns: 1fr; } .exercise-nav { position: static; display: flex; gap: .5rem; overflow-x: auto; padding-bottom: .35rem; } .exercise-nav__heading { display: none; } .exercise-nav button { flex: 0 0 auto; min-height: 48px; padding: .7rem 1rem; border-color: var(--hard-color-line); } .exercise-nav__text small { display: none; } .exercise-context { margin-bottom: 1.25rem; } }
</style>
