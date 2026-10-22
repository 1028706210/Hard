<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { courseStore } from "./course.store";
const route = useRoute();
const language = () => String(route.params.language ?? "");
const labels: Record<string, string> = { python: "Python", java: "Java", csharp: "C#", cpp: "C++" };
const query = ref("");
const loading = ref(true);
const error = ref("");
const modules = computed(() => courseStore.state.course?.language === language() ? courseStore.state.course.modules : []);
const lessonCount = computed(() => modules.value.reduce((sum, module) => sum + module.lessons.length, 0));
const filtered = computed(() => {
  const term = query.value.trim().toLowerCase();
  return modules.value.map(module => ({ ...module, lessons: module.lessons.filter(lesson =>
    !term || module.title.toLowerCase().includes(term) || lesson.title.toLowerCase().includes(term))
  })).filter(module => module.lessons.length);
});
async function load() {
  loading.value = true; error.value = ""; query.value = "";
  try { await courseStore.loadCourse(language()); }
  catch { error.value = "课程目录暂时无法读取，请重试。"; }
  finally { loading.value = false; }
}
onMounted(load);
watch(() => route.params.language, load);
</script>

<template>
  <section class="course-page">
    <header class="course-header">
      <div class="course-intro"><img v-if="labels[language()]" class="course-logo" :src="`/art/languages/${language() === 'cpp' ? 'cplusplus' : language()}.svg`" alt="" width="64" height="64"><div><p class="eyebrow">课程 / LEARNING PATH</p><h1 :aria-label="`课程：${language()}`">{{ labels[language()] ?? language() }} <span>学习路径</span></h1><p class="course-description">从概念理解到代码实践，选择一个模块开始学习。</p></div></div>
      <dl v-if="!loading && !error" class="course-summary"><div><dt>学习模块</dt><dd>{{ modules.length }}</dd></div><div><dt>完整课时</dt><dd>{{ lessonCount }}</dd></div></dl>
    </header>
    <nav class="course-languages" aria-label="切换学习语言"><RouterLink v-for="(label, key) in labels" :key="key" :to="`/course/${key}`">{{ label }}</RouterLink></nav>
    <RouterLink class="star-chain-entry" :to="`/constellations?language=${language()}`"><span>探索 {{ labels[language()] }} 知识星链</span><small>查看模块之间的联系与跨语言异同 →</small></RouterLink>
    <div class="course-directory-heading"><div><h2>课程目录</h2><p>一步一个概念，按自己的节奏前进。</p></div><label class="course-filter">查找课时<input v-model="query" type="search" placeholder="输入模块或课时名称" aria-label="查找课时"></label></div>
    <p v-if="loading" class="course-state" role="status">正在读取课程目录。</p>
    <div v-else-if="error" class="course-state" role="alert"><p>{{ error }}</p><button type="button" @click="load">重新读取课程</button></div>
    <p v-else-if="!filtered.length" class="course-state" role="status">没有匹配的课时，请换一个关键词。</p>
    <div v-else class="course-directory">
    <nav class="module-index" aria-label="学习模块索引"><p>学习模块 <span>{{ filtered.length }}</span></p><a v-for="module in filtered" :key="module.id" :href="`#course-module-${module.id}`"><span aria-hidden="true">{{ String(modules.findIndex(item => item.id === module.id) + 1).padStart(2, '0') }}</span>{{ module.title }}</a></nav>
    <nav class="course-modules" aria-label="课时目录">
      <section v-for="module in filtered" :id="`course-module-${module.id}`" :key="module.id" class="course-module">
        <header><span class="module-number">{{ String(modules.findIndex(item => item.id === module.id) + 1).padStart(2, '0') }}</span><div><h2>{{ module.title }}</h2><p>{{ module.lessons.length }} 节课时</p></div></header>
        <ul><li v-for="lesson in module.lessons" :key="lesson.id">
          <button v-if="lesson.locked" type="button" disabled :aria-label="`${lesson.title}，完成前置后解锁`">{{ lesson.title }}<small>完成前置后解锁</small></button>
          <RouterLink v-else :to="`/lesson/${lesson.id}`"><span class="lesson-title">{{ lesson.title }}</span><span aria-hidden="true">进入课时</span></RouterLink>
        </li></ul>
      </section>
    </nav>
    </div>
  </section>
</template>

<style scoped>
.course-page { display: grid; gap: 1.4rem; max-width: 78rem; margin: 0 auto; }
.course-header { display: flex; justify-content: space-between; align-items: center; gap: 2rem; padding: .5rem 0 1.5rem; border-bottom: 1px solid var(--hard-color-line); }
.course-intro { display: flex; align-items: center; gap: 1.5rem; min-width: 0; }
.course-logo { flex: 0 0 auto; width: 48px; height: 48px; }
.course-intro h1 span { font-weight: 400; color: var(--hard-color-muted); }
.course-directory-heading { display: flex; align-items: end; justify-content: space-between; gap: 1.5rem; margin-top: .5rem; }
.course-directory-heading h2 { font-size: 1.25rem; }
.course-directory-heading p { margin: .5rem 0 0; color: var(--hard-color-muted); font-size: .875rem; }
.course-filter { width: min(100%, 22rem); }
.star-chain-entry { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: .75rem; padding: .95rem 1.25rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-primary-strong); text-decoration: none; background: linear-gradient(110deg, color-mix(in srgb, var(--hard-color-primary) 9%, var(--hard-color-surface)), var(--hard-color-surface)); }
.star-chain-entry:hover { border-color: var(--hard-color-primary-strong); }
.eyebrow { margin: 0; color: var(--hard-color-primary-strong); font-size: .7rem; letter-spacing: .08em; }
h1 { margin: .4rem 0 .55rem; font-size: clamp(1.8rem, 2.7vw, 2.5rem); letter-spacing: -.04em; line-height: 1.35; }
.course-description { margin: 0; color: var(--hard-color-muted); }
.course-summary { display: flex; flex-shrink: 0; gap: 2rem; margin: 0; }
dt { color: var(--hard-color-muted); font-size: .75rem; } dd { margin: .3rem 0 0; font: 500 1.6rem ui-monospace, monospace; }
.course-languages { display: flex; flex-wrap: wrap; gap: .5rem; }
.course-languages a { display: inline-flex; align-items: center; padding: .55rem 1.15rem; min-height: 44px; border: 1px solid transparent; border-radius: var(--hard-radius-sm); color: var(--hard-color-muted); text-decoration: none; }
.course-languages a.router-link-active { color: var(--hard-color-text); border-color: var(--hard-color-primary); background: var(--hard-color-surface-raised); }
.course-filter { display: grid; gap: .5rem; color: var(--hard-color-muted); font-size: .875rem; }
input { width: 100%; padding: .85rem 1rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-surface); font: inherit; }
.course-directory { display: grid; grid-template-columns: 13rem minmax(0, 1fr); align-items: start; gap: 1.5rem; }
.module-index { position: sticky; top: 6rem; display: grid; gap: .2rem; }
.module-index p { display: flex; justify-content: space-between; margin: 0 0 .7rem; padding-inline: .75rem; color: var(--hard-color-muted); font-size: .75rem; }
.module-index a { display: flex; gap: .65rem; align-items: baseline; padding: .65rem .75rem; border-radius: var(--hard-radius-sm); color: var(--hard-color-muted); text-decoration: none; font-size: .82rem; line-height: 1.6; }
.module-index a span { color: var(--hard-color-primary-strong); font: .7rem ui-monospace, monospace; }
.module-index a:hover { color: var(--hard-color-text); background: var(--hard-color-surface); }
.course-modules { display: grid; align-items: start; gap: 1rem; }
.course-module { min-width: 0; padding: 1.35rem 1.5rem; scroll-margin-top: 6rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
.course-module header { display: flex; gap: 1rem; align-items: start; margin-bottom: 1.25rem; }
.module-number { color: var(--hard-color-primary-strong); font: 500 1.25rem ui-monospace, monospace; padding-top: .15rem; }
h2 { margin: 0; font-size: 1.05rem; } .course-module header p { margin: .35rem 0 0; color: var(--hard-color-muted); font-size: .8rem; }
ul { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 1.5rem; padding: 0; margin: 0; list-style: none; } li { min-width: 0; border-top: 1px solid var(--hard-color-line); }
li a, li button { display: flex; justify-content: space-between; align-items: center; gap: .75rem; width: 100%; min-height: 52px; padding: .75rem .25rem; border: 0; color: var(--hard-color-text); background: transparent; text-align: left; text-decoration: none; font: inherit; font-size: .85rem; line-height: 1.65; }
li a > span[aria-hidden], small { flex-shrink: 0; color: var(--hard-color-muted); font-size: .75rem; }
li a:hover { color: var(--hard-color-primary-strong); } li button:disabled { color: var(--hard-color-muted); cursor: not-allowed; }
.course-state { padding: 2rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-md); color: var(--hard-color-muted); }
.course-state button { padding: .75rem 1rem; color: var(--hard-color-text); background: var(--hard-color-primary); border: 0; border-radius: var(--hard-radius-sm); }
@media (max-width: 64rem) { .course-directory { grid-template-columns: 1fr; } .module-index { position: static; display: flex; gap: .4rem; overflow-x: auto; padding-bottom: .4rem; } .module-index p { display: none; } .module-index a { flex: 0 0 auto; padding: .65rem .8rem; border: 1px solid var(--hard-color-line); } }
@media (max-width: 48rem) { .course-header { flex-direction: column; align-items: start; gap: 1.25rem; padding: .5rem 0 1.25rem; } .course-intro { gap: 1rem; } .course-logo { width: 40px; height: 40px; } .course-intro h1 span { display: block; font-size: 1.1rem; margin-top: .4rem; } .course-directory-heading { align-items: stretch; flex-direction: column; gap: 1rem; } .course-filter { width: 100%; } .course-summary { gap: 2.5rem; } .course-modules, ul { grid-template-columns: 1fr; } .course-module { padding: 1.15rem; } li a > span[aria-hidden] { display: none; } .star-chain-entry small { line-height: 1.6; } }
</style>
