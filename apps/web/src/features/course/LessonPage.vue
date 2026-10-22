<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import LessonContent from "./LessonContent.vue";
import LessonNav from "./LessonNav.vue";
import LessonTools from "./LessonTools.vue";
import { courseStore } from "./course.store";

const route = useRoute();
const navigationOpen = ref(false);
const lessonId = () => String(route.params.lessonId ?? "");
const currentModule = computed(() => courseStore.state.course?.modules.find(module => module.lessons.some(lesson => lesson.id === lessonId())));
const lessonPosition = computed(() => (currentModule.value?.lessons.findIndex(lesson => lesson.id === lessonId()) ?? -1) + 1);
const adjacentLessons = computed(() => {
  const lessons = courseStore.state.course?.modules.flatMap(module => module.lessons) ?? [];
  const index = lessons.findIndex(lesson => lesson.id === lessonId());
  return { previous: index > 0 ? lessons[index - 1] : undefined, next: index >= 0 ? lessons[index + 1] : undefined };
});
let progressTimer: ReturnType<typeof setTimeout> | undefined;
async function load() {
  await courseStore.loadLesson(lessonId()).catch(() => undefined);
  if (courseStore.state.lesson) await courseStore.loadCourse(courseStore.state.lesson.language ?? "python").catch(() => undefined);
  if (courseStore.state.lesson) await courseStore.saveProgress(0, 0).catch(() => undefined);
}
function saveReadingPosition() {
  if (!courseStore.state.lesson) return;
  if (progressTimer) clearTimeout(progressTimer);
  progressTimer = setTimeout(() => {
    void courseStore.saveProgress(Math.max(0, Math.floor(window.scrollY)), 0).catch(() => undefined);
  }, 250);
}
async function saveNote() { await courseStore.saveNote().catch(() => undefined); }
async function retryNote() { await courseStore.retryNote().catch(() => undefined); }
async function toggleFavorite() { await courseStore.setFavorite(!courseStore.state.favorite).catch(() => undefined); }
onMounted(() => {
  void load();
  window.addEventListener("scroll", saveReadingPosition, { passive: true });
});
onUnmounted(() => {
  window.removeEventListener("scroll", saveReadingPosition);
  if (progressTimer) clearTimeout(progressTimer);
});
watch(() => route.params.lessonId, load);
</script>

<template>
  <section class="lesson-page">
    <header v-if="courseStore.state.lesson" class="lesson-page__context">
      <div><RouterLink :to="`/course/${courseStore.state.lesson.language ?? 'python'}`">课程目录</RouterLink><span aria-hidden="true"> / </span><span>{{ currentModule?.title ?? courseStore.state.lesson.title }}</span></div>
      <p v-if="currentModule">模块内第 {{ lessonPosition }} / {{ currentModule.lessons.length }} 课</p>
    </header>
    <button class="lesson-page__directory" type="button" aria-label="打开课时目录" @click="navigationOpen = true">课时目录</button>
    <LessonNav v-if="courseStore.state.course" :modules="courseStore.state.course.modules" :active-lesson-id="lessonId()" :open="navigationOpen" @close="navigationOpen = false" />
    <p v-else class="lesson-page__placeholder">{{ courseStore.state.lesson ? "" : `课时：${lessonId()}` }}</p>
    <LessonContent v-if="courseStore.state.lesson" :lesson="courseStore.state.lesson" />
    <LessonTools
      v-if="courseStore.state.lesson"
      :model-value="courseStore.state.noteDraft"
      :favorite="courseStore.state.favorite"
      :sync-status="courseStore.state.syncStatus"
      @update:model-value="courseStore.setNoteDraft"
      @save="saveNote"
      @retry="retryNote"
      @favorite="toggleFavorite"
    />
    <nav v-if="courseStore.state.lesson" class="lesson-page__adjacent" aria-label="相邻课时">
      <RouterLink v-if="adjacentLessons.previous && !adjacentLessons.previous.locked" :to="`/lesson/${adjacentLessons.previous.id}`"><small>← 上一课</small><span>{{ adjacentLessons.previous.title }}</span></RouterLink>
      <RouterLink v-if="adjacentLessons.next && !adjacentLessons.next.locked" class="lesson-page__next" :to="`/lesson/${adjacentLessons.next.id}`"><small>下一课 →</small><span>{{ adjacentLessons.next.title }}</span></RouterLink>
    </nav>
  </section>
</template>

<style scoped>
.lesson-page { display: grid; grid-template-columns: 14.5rem minmax(0, 1fr); align-items: start; gap: 1.25rem 1.75rem; max-width: 78rem; margin: 0 auto; }
.lesson-page__context { grid-column: 1 / -1; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: .75rem; padding-bottom: .5rem; color: var(--hard-color-muted); font-size: .8rem; line-height: 1.7; }
.lesson-page__context a { color: var(--hard-color-muted); text-decoration: none; }
.lesson-page__context a:hover { color: var(--hard-color-primary-strong); }
.lesson-page__context p { margin: 0; font-variant-numeric: tabular-nums; }
.lesson-page :deep(.lesson-nav) { grid-column: 1; grid-row: 2 / span 3; }
.lesson-page :deep(.lesson-content), .lesson-page :deep(.lesson-tools), .lesson-page__adjacent { grid-column: 2; }
.lesson-page__directory { display: none; }
.lesson-page__placeholder { color: var(--hard-color-muted); }
.lesson-page__adjacent { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
.lesson-page__adjacent a { display: grid; gap: .5rem; min-height: 84px; padding: 1.1rem 1.25rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); text-decoration: none; font-size: .9rem; line-height: 1.6; }
.lesson-page__adjacent a:hover { border-color: var(--hard-color-primary-strong); background: var(--hard-color-surface); }
.lesson-page__adjacent small { color: var(--hard-color-muted); font-size: .75rem; }
.lesson-page__next { grid-column: 2; text-align: right; }
@media (max-width: 64rem) { .lesson-page { grid-template-columns: 12rem minmax(0, 1fr); gap: 1rem; } }
@media (max-width: 52rem) { .lesson-page { display: block; } .lesson-page__context { margin-bottom: 1rem; } .lesson-page__directory { display: inline-flex; align-items: center; min-height: var(--hard-touch-target); margin-bottom: 1rem; padding: 0 1rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-surface); font: inherit; } .lesson-page > :not(.lesson-page__directory) { margin-bottom: 1rem; } .lesson-page__adjacent { gap: .6rem; } .lesson-page__adjacent a { padding: 1rem; font-size: .8rem; } }
</style>
