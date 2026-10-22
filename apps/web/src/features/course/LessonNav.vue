<script setup lang="ts">
import type { CourseModule } from "./course.store";

defineProps<{ modules: readonly CourseModule[]; open: boolean; activeLessonId?: string }>();
defineEmits<{ close: [] }>();
</script>

<template>
  <nav class="lesson-nav" :class="{ 'lesson-nav--open': open }" aria-label="课时目录">
    <button class="lesson-nav__close" type="button" aria-label="关闭课时目录" @click="$emit('close')">关闭</button>
    <p class="lesson-nav__heading">学习目录 <span>{{ modules.length }} 个模块</span></p>
    <details v-for="(module, index) in modules" :key="module.id" :open="activeLessonId ? module.lessons.some(lesson => lesson.id === activeLessonId) : index === 0">
      <summary><span class="lesson-nav__number">{{ String(index + 1).padStart(2, '0') }}</span><span>{{ module.title }}</span><span class="lesson-nav__chevron" aria-hidden="true">⌄</span></summary>
      <ul>
        <li v-for="lesson in module.lessons" :key="lesson.id">
          <button v-if="lesson.locked" type="button" disabled :aria-label="`${lesson.title}，完成前置后解锁`">{{ lesson.title }}<small>完成前置后解锁</small></button>
          <RouterLink v-else :to="`/lesson/${lesson.id}`" @click="$emit('close')">{{ lesson.title }}</RouterLink>
        </li>
      </ul>
    </details>
  </nav>
</template>

<style scoped>
.lesson-nav { align-self: start; padding: 1rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
.lesson-nav__heading { display: flex; flex-wrap: wrap; gap: .4rem; justify-content: space-between; margin: .25rem 0 1rem; color: var(--hard-color-text); font-size: .8rem; }
.lesson-nav__heading > span { color: var(--hard-color-muted); font-size: .7rem; }
summary { display: flex; align-items: baseline; gap: .55rem; min-height: 44px; padding: .7rem .25rem; color: var(--hard-color-text); cursor: pointer; font-size: .8rem; font-weight: 600; line-height: 1.6; list-style: none; }
summary::-webkit-details-marker { display: none; }
.lesson-nav__number { color: var(--hard-color-primary-strong); font: .7rem ui-monospace, monospace; }
.lesson-nav__chevron { margin-left: auto; color: var(--hard-color-muted); transition: transform .18s ease; }
details[open] .lesson-nav__chevron { transform: rotate(180deg); }
ul { display: grid; gap: var(--hard-space-1); margin: 0; padding: 0; list-style: none; }
a, button { display: grid; width: 100%; min-height: var(--hard-touch-target); padding: var(--hard-space-2); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: transparent; font: inherit; text-align: left; text-decoration: none; }
a:hover, a.router-link-active { background: var(--hard-color-surface-raised); }
button:disabled { color: var(--hard-color-muted); cursor: not-allowed; }
small { margin-top: var(--hard-space-1); font-size: var(--hard-text-xs); }
.lesson-nav__close { display: none; margin-left: auto; color: var(--hard-color-muted); }
.lesson-nav details + details { margin-top: .4rem; padding-top: .4rem; border-top: 1px solid var(--hard-color-line); }
.lesson-nav ul { padding-bottom: .75rem; }
.lesson-nav a { color: var(--hard-color-muted); font-size: .8rem; line-height: 1.65; }
.lesson-nav a.router-link-active { color: var(--hard-color-primary-strong); box-shadow: inset 2px 0 var(--hard-color-primary-strong); }
@media (min-width: 52.01rem) { .lesson-nav { position: sticky; top: 6rem; max-height: calc(100dvh - 7rem); overflow-y: auto; scrollbar-width: thin; } }

@media (max-width: 52rem) {
  .lesson-nav { position: fixed; z-index: 60; top: 0; right: 0; bottom: 0; width: min(19rem, calc(100vw - var(--hard-space-5))); display: none; overflow-y: auto; border-radius: 0; box-shadow: var(--hard-shadow-raised); }
  .lesson-nav--open { display: block; }
  .lesson-nav__close { display: block; }
}
@media (prefers-reduced-motion: reduce) { .lesson-nav__chevron { transition: none; } }
</style>
