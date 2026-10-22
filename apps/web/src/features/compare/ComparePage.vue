<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { requestJson } from "../../api/client";

const languages = ["python", "java", "csharp", "cpp"] as const;
type Language = (typeof languages)[number];
type CompareSlot = {
  status: "available" | "missing";
  summary: string;
  difference: string;
  code: string | null;
  lesson_id: string | null;
  lesson_title: string | null;
  note: string | null;
};
type CompareConcept = {
  id: string;
  name: string;
  description: string;
  slots: Record<Language, CompareSlot>;
};

const route = useRoute();
const router = useRouter();
const concepts = ref<CompareConcept[]>([]);
const filter = computed({
  get: () => typeof route.query.filter === "string" ? route.query.filter : "",
  set: (value: string) => {
    void router.replace({ query: { ...route.query, filter: value || undefined, page: undefined } });
  },
});
const loading = ref(true);
const error = ref("");
const pageSize = 4;

const languageLabels: Record<Language, string> = {
  python: "Python",
  java: "Java",
  csharp: "C#",
  cpp: "C++",
};

const visibleConcepts = computed(() => {
  const query = filter.value.trim().toLowerCase();
  if (!query) return concepts.value;
  return concepts.value.filter(
    (concept) => concept.id.toLowerCase().includes(query) || concept.name.toLowerCase().includes(query),
  );
});
const pageCount = computed(() => Math.ceil(visibleConcepts.value.length / pageSize));
const page = computed({
  get: () => {
    const requested = typeof route.query.page === "string" ? Number(route.query.page) : 1;
    const selected = Number.isSafeInteger(requested) && requested > 0 ? requested : 1;
    return Math.min(selected, Math.max(1, pageCount.value));
  },
  set: (value: number) => {
    void router.replace({ query: { ...route.query, page: value > 1 ? String(value) : undefined } });
  },
});
const pageConcepts = computed(() => visibleConcepts.value.slice((page.value - 1) * pageSize, page.value * pageSize));

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const payload = await requestJson<{ concepts: CompareConcept[] }>("/api/compare/concepts");
    concepts.value = payload.concepts;
  } catch {
    error.value = "当前无法读取跨语言对照数据，请稍后重试。";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="compare-page" aria-labelledby="compare-title">
    <header>
      <p>同一个概念，四种语言的表达</p>
      <h1 id="compare-title">跨语言对照</h1>
      <p class="page-intro">先找到一个概念，再读懂四种语言的相同与不同。</p>
    </header>
    <p v-if="error" class="notice" role="alert">{{ error }}</p>
    <p v-else-if="loading" class="state" role="status">正在加载对照数据…</p>
    <p v-else-if="!concepts.length" class="state" data-empty-state>暂无可对照的课程概念。</p>
    <template v-else>
      <div class="filter-row" role="search">
        <label for="concept-filter">筛选概念</label>
        <input
          id="concept-filter"
          v-model="filter"
          data-concept-filter
          type="search"
          placeholder="搜索概念名称或 ID，例如：变量、variables"
          autocomplete="off"
        />
        <span class="count" role="status">{{ visibleConcepts.length }} / {{ concepts.length }} 个概念</span>
      </div>
      <div v-if="pageCount > 1" class="page-navigation" aria-label="对照概念分页">
        <p>每页 4 个概念 · 第 {{ page }} / {{ pageCount }} 页</p>
        <div><button type="button" :disabled="page === 1" @click="page--">← 上一页</button><button data-next-concepts type="button" :disabled="page >= pageCount" @click="page++">下一页 →</button></div>
      </div>
      <p v-if="!visibleConcepts.length" class="state" data-empty-state>没有匹配当前筛选的概念。</p>
      <section
        v-for="concept in pageConcepts"
        :key="concept.id"
        class="concept-row"
        :data-concept-card="concept.id"
        :aria-label="`${concept.name} 对照`"
      >
        <header class="concept-head">
          <h2>{{ concept.name }}</h2>
          <p><code>{{ concept.id }}</code> · {{ concept.description }}</p>
        </header>
        <div class="language-grid">
          <article
            v-for="language in languages"
            :key="language"
            :data-language="language"
            :class="{ 'is-missing': concept.slots[language].status === 'missing' }"
          >
            <h3>{{ languageLabels[language] }}</h3>
            <template v-if="concept.slots[language].status === 'available'">
              <p class="summary">{{ concept.slots[language].summary }}</p>
              <p class="difference">{{ concept.slots[language].difference }}</p>
              <pre><code>{{ concept.slots[language].code }}</code></pre>
              <a v-if="concept.slots[language].lesson_id" :href="`/lesson/${concept.slots[language].lesson_id}`">
                课时：{{ concept.slots[language].lesson_title ?? concept.slots[language].lesson_id }}
              </a>
            </template>
            <template v-else>
              <p class="unavailable" data-missing-slot>缺失：{{ languageLabels[language] }} 路线内暂无可对照的标注课时。</p>
              <p class="note">{{ concept.slots[language].note }}</p>
            </template>
          </article>
        </div>
      </section>
      <nav v-if="pageCount > 1" class="page-navigation" aria-label="对照概念页尾分页"><p role="status">正在阅读第 {{ (page - 1) * pageSize + 1 }}–{{ Math.min(page * pageSize, visibleConcepts.length) }} 个概念，共 {{ visibleConcepts.length }} 个</p><div><button type="button" :disabled="page === 1" @click="page--">← 上一页</button><button type="button" :disabled="page >= pageCount" @click="page++">下一页 →</button></div></nav>
    </template>
  </section>
</template>

<style scoped>
.compare-page { display: grid; gap: var(--hard-space-5); max-width: 76rem; margin: 0 auto; }
header p { margin: 0; color: var(--hard-color-primary-strong); }
h1 { margin: var(--hard-space-1) 0 0; font-size: clamp(2rem, 5vw, 3.5rem); }
.filter-row { display: flex; flex-wrap: wrap; align-items: center; gap: var(--hard-space-3); }
.filter-row label { font-weight: 700; }
.filter-row input { min-height: var(--hard-touch-target); flex: 1 1 16rem; padding: 0 var(--hard-space-3); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-surface); font: inherit; }
.filter-row .count { color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
.concept-row { padding: 1.5rem; border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
.concept-head h2 { margin: 0 0 var(--hard-space-1); color: var(--hard-color-cyan); font-size: var(--hard-text-lg); }
.concept-head p { margin: 0 0 var(--hard-space-3); color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
.language-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--hard-space-3); }
article { display: grid; align-content: start; gap: .85rem; min-width: 0; min-height: 10rem; padding: 1rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); background: transparent; line-height: 1.8; overflow-wrap: anywhere; }
article.is-missing { background: transparent; border: 0.0625rem dashed var(--hard-color-line); }
h3 { margin: 0; color: var(--hard-color-muted); font-size: var(--hard-text-sm); text-transform: uppercase; }
article p { margin: 0; color: var(--hard-color-text); font-size: var(--hard-text-sm); }
.summary { font-weight: 700; }
article .difference, article .note { color: var(--hard-color-muted); }
pre { margin: 0; padding: var(--hard-space-2); overflow-x: auto; border-radius: var(--hard-radius-sm); background: var(--hard-color-space); }
pre code { display: block; font-family: ui-monospace, Consolas, monospace; font-size: var(--hard-text-sm); white-space: pre; }
a { color: var(--hard-color-primary-strong); font-weight: 700; }
.unavailable { color: var(--hard-color-amber); font-weight: 700; }
.state, .notice { margin: 0; padding: var(--hard-space-4); border-radius: var(--hard-radius-sm); color: var(--hard-color-muted); background: var(--hard-color-surface); }
.notice { color: var(--hard-color-danger); }
@media (max-width: 70rem) { .language-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 42rem) { .language-grid { grid-template-columns: 1fr; } }
.page-intro { margin-top: .85rem; max-width: 42rem; color: var(--hard-color-muted); line-height: 1.8; }
.filter-row { padding: 1.25rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
.filter-row label { font-size: .875rem; }
.concept-row { padding: clamp(1.1rem, 3vw, 2rem); border-top: 2px solid color-mix(in srgb, var(--hard-color-cyan) 45%, var(--hard-color-line)); }
.concept-head { margin-bottom: 1.25rem; }
.concept-head h2 { font-size: 1.4rem; color: var(--hard-color-text); }
.concept-head code { color: var(--hard-color-cyan); font-size: .8rem; }
.concept-head p { line-height: 1.8; }
.language-grid article { padding: 1.25rem; background: color-mix(in srgb, var(--hard-color-space) 55%, transparent); }
.language-grid h3 { color: var(--hard-color-cyan); letter-spacing: .08em; }
pre { padding: 1rem; border: 1px solid var(--hard-color-line); }
.page-navigation { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: .75rem; }
.page-navigation p { margin: 0; color: var(--hard-color-muted); font-size: .875rem; }
.page-navigation > div { display: flex; gap: .5rem; }
.page-navigation button { min-height: var(--hard-touch-target); padding: .5rem 1rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-surface); font: inherit; cursor: pointer; }
.page-navigation button:disabled { opacity: .4; cursor: default; }
.page-navigation button:not(:disabled):hover { border-color: var(--hard-color-cyan); }
</style>
