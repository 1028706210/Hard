<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import LessonContent from "./LessonContent.vue";
import LessonNav from "./LessonNav.vue";
import LessonTools from "./LessonTools.vue";
import { courseStore } from "./course.store";

const route = useRoute();
const navigationOpen = ref(false);
const lessonId = () => String(route.params.lessonId ?? "");
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
    <button class="lesson-page__directory" type="button" aria-label="打开课时目录" @click="navigationOpen = true">课时目录</button>
    <LessonNav v-if="courseStore.state.course" :modules="courseStore.state.course.modules" :open="navigationOpen" @close="navigationOpen = false" />
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
  </section>
</template>

<style scoped>
.lesson-page { display: grid; grid-template-columns: minmax(13rem, 16rem) minmax(0, 1fr) minmax(15rem, 20rem); gap: var(--hard-space-4); max-width: 100rem; margin: 0 auto; }
.lesson-page__directory { display: none; }
.lesson-page__placeholder { color: var(--hard-color-muted); }

@media (max-width: 70rem) { .lesson-page { grid-template-columns: minmax(12rem, 15rem) minmax(0, 1fr); } .lesson-page > :last-child { grid-column: 2; } }
@media (max-width: 52rem) { .lesson-page { display: block; } .lesson-page__directory { display: inline-flex; min-height: var(--hard-touch-target); margin-bottom: var(--hard-space-3); padding: 0 var(--hard-space-3); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; } .lesson-page > :not(.lesson-page__directory) { margin-bottom: var(--hard-space-3); } }
</style>
