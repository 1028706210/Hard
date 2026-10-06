<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useRoute } from "vue-router";

import LessonNav from "./LessonNav.vue";
import { courseStore } from "./course.store";

const route = useRoute();
const language = () => String(route.params.language ?? "");
async function load() { await courseStore.loadCourse(language()).catch(() => undefined); }
onMounted(load);
watch(() => route.params.language, load);
</script>

<template>
  <section class="course-page">
    <header><p>学习路线</p><h1>课程：{{ language() }}</h1><span v-if="courseStore.state.course?.fixture_only">当前为课程夹具，完整路线将在内容批次替换。</span></header>
    <LessonNav v-if="courseStore.state.course" :modules="courseStore.state.course.modules" :open="true" />
    <p v-else class="course-page__empty">课程目录加载后将在此显示。</p>
  </section>
</template>

<style scoped>
.course-page { display: grid; gap: var(--hard-space-5); max-width: 70rem; margin: 0 auto; }
header { padding: var(--hard-space-5); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
p { color: var(--hard-color-primary-strong); } h1 { margin: var(--hard-space-1) 0; } span, .course-page__empty { color: var(--hard-color-muted); }
</style>
