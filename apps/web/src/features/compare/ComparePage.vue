<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { requestJson } from "../../api/client";

interface LessonReference { id: string; }
interface CatalogCourse { language: string; modules: Array<{ lessons: LessonReference[] }>; }
interface Lesson { id: string; language: string; title: string; concepts: string[]; }
const languages = ["python", "java", "csharp", "cpp"] as const;
const lessons = ref<Lesson[]>([]);
const error = ref("");

const concepts = computed(() => [...new Set(lessons.value.flatMap((lesson) => lesson.concepts))].sort());
function lessonFor(language: string, concept: string) { return lessons.value.find((lesson) => lesson.language === language && lesson.concepts.includes(concept)); }

async function load() {
  try {
    const catalog = await requestJson<{ courses: CatalogCourse[] }>("/api/content/catalog");
    const references = catalog.courses.flatMap((course) => course.modules.flatMap((module) => module.lessons.map((lesson) => ({ language: course.language, id: lesson.id }))));
    lessons.value = await Promise.all(references.map(async (reference) => requestJson<Lesson>(`/api/content/lessons/${reference.id}`)));
  } catch { error.value = "当前无法读取可对照的课程内容。"; }
}

onMounted(load);
</script>

<template>
  <section class="compare-page" aria-labelledby="compare-title">
    <header><p>按稳定 concept ID 对齐</p><h1 id="compare-title">跨语言对照</h1></header>
    <p v-if="error" class="notice" role="alert">{{ error }}</p>
    <p v-else-if="!concepts.length" class="empty-state">暂无可对照的课程概念。</p>
    <section v-for="concept in concepts" :key="concept" class="concept-row" :aria-label="`${concept} 对照`"><h2>{{ concept }}</h2><div class="language-grid"><article v-for="language in languages" :key="language" :data-language="language"><h3>{{ language }}</h3><template v-if="lessonFor(language, concept)"><a :href="`/lesson/${lessonFor(language, concept)?.id}`">{{ lessonFor(language, concept)?.title }}</a><p>已有当前课程内容</p></template><p v-else class="unavailable">尚无内容</p></article></div></section>
  </section>
</template>

<style scoped>
.compare-page { display: grid; gap: var(--hard-space-5); max-width: 76rem; margin: 0 auto; } header p { margin: 0; color: var(--hard-color-primary-strong); } h1 { margin: var(--hard-space-1) 0 0; font-size: clamp(2rem, 5vw, 3.5rem); } .concept-row { padding: var(--hard-space-4); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); } h2 { margin: 0 0 var(--hard-space-3); color: var(--hard-color-cyan); font-size: var(--hard-text-lg); } .language-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--hard-space-2); } article { min-height: 8.5rem; padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); background: var(--hard-color-surface-raised); } h3 { margin: 0 0 var(--hard-space-3); color: var(--hard-color-muted); font-size: var(--hard-text-sm); text-transform: uppercase; } a { color: var(--hard-color-primary-strong); font-weight: 700; } article p { margin: var(--hard-space-2) 0 0; color: var(--hard-color-muted); font-size: var(--hard-text-sm); } .unavailable { color: var(--hard-color-amber); } .empty-state, .notice { margin: 0; padding: var(--hard-space-4); border-radius: var(--hard-radius-sm); color: var(--hard-color-muted); background: var(--hard-color-surface); } .notice { color: var(--hard-color-danger); }
@media (max-width: 48rem) { .language-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } } @media (max-width: 28rem) { .language-grid { grid-template-columns: 1fr; } }
</style>
