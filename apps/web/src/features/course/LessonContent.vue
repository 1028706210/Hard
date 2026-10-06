<script setup lang="ts">
import type { Lesson } from "./course.store";

defineProps<{ lesson: Lesson }>();
</script>

<template>
  <article class="lesson-content">
    <h1>{{ lesson.title }}</h1>
    <div class="lesson-content__body" v-html="lesson.rendered_html"></div>
    <footer>
      <a :href="lesson.source_url" target="_blank" rel="noreferrer">来源：菜鸟教程</a>
      <span>快照：{{ lesson.source_snapshot_date }}</span>
    </footer>
  </article>
</template>

<style scoped>
.lesson-content { min-width: 0; padding: clamp(var(--hard-space-4), 4vw, var(--hard-space-8)); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
h1 { margin-top: 0; font-size: clamp(1.75rem, 4vw, 3rem); }
.lesson-content__body :deep(pre) { overflow-x: auto; padding: var(--hard-space-4); border-radius: var(--hard-radius-sm); background: var(--hard-color-space); }
.lesson-content__body :deep(code) { overflow-wrap: anywhere; }
.lesson-content__body :deep(a), footer a { color: var(--hard-color-cyan); }
footer { display: flex; flex-wrap: wrap; gap: var(--hard-space-3); margin-top: var(--hard-space-6); padding-top: var(--hard-space-3); border-top: 0.0625rem solid var(--hard-color-line); color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
</style>
