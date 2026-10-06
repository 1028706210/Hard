<script setup lang="ts">
import type { CourseModule } from "./course.store";

defineProps<{ modules: readonly CourseModule[]; open: boolean }>();
defineEmits<{ close: [] }>();
</script>

<template>
  <nav class="lesson-nav" :class="{ 'lesson-nav--open': open }" aria-label="课时目录">
    <button class="lesson-nav__close" type="button" aria-label="关闭课时目录" @click="$emit('close')">关闭</button>
    <section v-for="module in modules" :key="module.id">
      <h2>{{ module.title }}</h2>
      <ul>
        <li v-for="lesson in module.lessons" :key="lesson.id">
          <button v-if="lesson.locked" type="button" disabled :aria-label="`${lesson.title}，完成前置后解锁`">{{ lesson.title }}<small>完成前置后解锁</small></button>
          <RouterLink v-else :to="`/lesson/${lesson.id}`" @click="$emit('close')">{{ lesson.title }}</RouterLink>
        </li>
      </ul>
    </section>
  </nav>
</template>

<style scoped>
.lesson-nav { align-self: start; padding: var(--hard-space-4); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
h2 { margin: 0 0 var(--hard-space-2); font-size: var(--hard-text-md); }
ul { display: grid; gap: var(--hard-space-1); margin: 0; padding: 0; list-style: none; }
a, button { display: grid; width: 100%; min-height: var(--hard-touch-target); padding: var(--hard-space-2); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: transparent; font: inherit; text-align: left; text-decoration: none; }
a:hover, a.router-link-active { background: var(--hard-color-surface-raised); }
button:disabled { color: var(--hard-color-muted); cursor: not-allowed; }
small { margin-top: var(--hard-space-1); font-size: var(--hard-text-xs); }
.lesson-nav__close { display: none; margin-left: auto; color: var(--hard-color-muted); }

@media (max-width: 52rem) {
  .lesson-nav { position: fixed; z-index: 20; top: 0; right: 0; bottom: 0; width: min(19rem, calc(100vw - var(--hard-space-5))); display: none; overflow-y: auto; border-radius: 0; box-shadow: var(--hard-shadow-raised); }
  .lesson-nav--open { display: block; }
  .lesson-nav__close { display: block; }
}
</style>
