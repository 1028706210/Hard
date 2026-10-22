<script setup lang="ts">
import type { Lesson } from "./course.store";
import { computed } from "vue";

const props = defineProps<{ lesson: Lesson }>();
const article = computed(() => {
  const document = new DOMParser().parseFromString(props.lesson.rendered_html, "text/html");
  const first = document.body.firstElementChild;
  if (first?.tagName === "H1" && first.textContent?.trim() === props.lesson.title.trim()) first.remove();
  const sections = [...document.body.querySelectorAll("h2, h3")].map((heading, index) => {
    const id = `lesson-section-${index + 1}`;
    heading.id = id;
    return { id, title: heading.textContent?.trim() ?? "", nested: heading.tagName === "H3" };
  }).filter(section => section.title);
  return { html: document.body.innerHTML, sections };
});
</script>

<template>
  <article class="lesson-content">
    <div class="lesson-content__reading">
    <p class="lesson-kicker">课时阅读 <span aria-hidden="true">/</span> READ & UNDERSTAND</p>
    <h1>{{ lesson.title }}</h1>
    <nav v-if="article.sections.length" class="lesson-sections" aria-label="本课章节">
      <p>本课内容</p>
      <a v-for="section in article.sections" :key="section.id" :href="`#${section.id}`" :class="{ 'is-nested': section.nested }">{{ section.title }}</a>
    </nav>
    <div class="lesson-content__body" v-html="article.html"></div>
    <RouterLink class="lesson-practice" :to="`/assessment/${lesson.id}`">完成阅读，进入本课练习</RouterLink>
    <footer>
      <a :href="lesson.source_url" target="_blank" rel="noreferrer">来源：菜鸟教程</a>
      <span>快照：{{ lesson.source_snapshot_date }}</span>
    </footer>
    </div>
  </article>
</template>

<style scoped>
.lesson-content { min-width: 0; padding: clamp(1.25rem, 3.2vw, 3rem); border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
h1 { margin: .65rem 0 1.75rem; font-size: clamp(1.85rem, 2.9vw, 2.6rem); line-height: 1.35; letter-spacing: -.035em; }
.lesson-kicker { margin: 0; color: var(--hard-color-muted); font-size: .7rem; letter-spacing: .08em; }
.lesson-kicker span { margin-inline: .5rem; color: var(--hard-color-primary-strong); }
.lesson-content__reading { max-width: 44rem; margin-inline: auto; }
.lesson-sections { display: flex; flex-wrap: wrap; gap: .5rem .85rem; margin-bottom: 2rem; padding: 1rem 0; border-block: 1px solid var(--hard-color-line); }
.lesson-sections p { flex-basis: 100%; margin: 0 0 .15rem; color: var(--hard-color-muted); font-size: .75rem; }
.lesson-sections a { color: var(--hard-color-text); font-size: .85rem; text-decoration-color: var(--hard-color-line); text-underline-offset: .3rem; }
.lesson-sections a:hover { color: var(--hard-color-primary-strong); }
.lesson-sections a.is-nested { color: var(--hard-color-muted); }
.lesson-content__body { font-size: 1.025rem; line-height: 1.95; overflow-wrap: anywhere; color: var(--hard-color-text); }
.lesson-content__body :deep(p), .lesson-content__body :deep(ul), .lesson-content__body :deep(ol) { margin-block: 1.25rem; }
.lesson-content__body :deep(h2), .lesson-content__body :deep(h3) { color: var(--hard-color-text); scroll-margin-top: 7rem; }
.lesson-content__body :deep(blockquote) { margin: 1.5rem 0; padding: .25rem 1.25rem; border-left: 2px solid var(--hard-color-cyan); color: var(--hard-color-muted); }
.lesson-content__body :deep(img) { max-width: 100%; height: auto; }
.lesson-content__body :deep(h2) { margin-top: 2rem; font-size: 1.4rem; line-height: 1.5; }
.lesson-content__body :deep(h3) { margin-top: 1.75rem; font-size: 1.15rem; }
.lesson-content__body :deep(table) { display: block; max-width: 100%; overflow-x: auto; border-collapse: collapse; }
.lesson-content__body :deep(td), .lesson-content__body :deep(th) { padding: .75rem; border: 1px solid var(--hard-color-line); }
.lesson-practice { display: inline-flex; align-items: center; justify-content: center; min-height: 48px; margin-top: 1.5rem; padding: .75rem 1.25rem; border: 1px solid var(--hard-color-primary); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); text-decoration: none; }
.lesson-content__body :deep(pre) { overflow-x: auto; padding: 1.25rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); background: var(--hard-color-space); line-height: 1.75; font-size: .9rem; }
.lesson-content__body :deep(code) { font-size: .88em; overflow-wrap: anywhere; }
.lesson-content__body :deep(pre code) { font-size: inherit; overflow-wrap: normal; }
.lesson-content__body :deep(a), footer a { color: var(--hard-color-cyan); }
footer { display: flex; flex-wrap: wrap; gap: var(--hard-space-3); margin-top: var(--hard-space-6); padding-top: var(--hard-space-3); border-top: 0.0625rem solid var(--hard-color-line); color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
@media (max-width: 40rem) { .lesson-content { padding: 1.25rem; } .lesson-content__body { font-size: 1rem; line-height: 1.9; } .lesson-content__body :deep(pre) { padding: 1rem; font-size: .8rem; } .lesson-practice { display: flex; } }
</style>
