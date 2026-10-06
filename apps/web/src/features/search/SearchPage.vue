<script setup lang="ts">
import { ref } from "vue";

import { requestJson } from "../../api/client";

interface SearchResult { source_type: string; language: string; lesson_id: string; title: string; snippet: string; anchor: string; }

const query = ref("");
const results = ref<SearchResult[]>([]);
const searched = ref(false);
const error = ref("");

async function search() {
  searched.value = true;
  error.value = "";
  if (!query.value.trim()) { results.value = []; return; }
  try {
    const response = await requestJson<{ results: SearchResult[] }>(`/api/search?q=${encodeURIComponent(query.value.trim())}`);
    results.value = response.results;
  } catch { error.value = "搜索暂时不可用，请稍后重试。"; }
}

function resultLink(result: SearchResult) {
  return `/lesson/${result.lesson_id}${result.anchor ? `#${encodeURIComponent(result.anchor)}` : ""}`;
}
</script>

<template>
  <section class="search-page" aria-labelledby="search-title">
    <header><p>课程、知识点、笔记与收藏</p><h1 id="search-title">全文搜索</h1></header>
    <form class="search-form" @submit.prevent="search"><label for="search-query">搜索课程内容</label><div><input id="search-query" v-model="query" aria-label="搜索课程内容" type="search" autocomplete="off" placeholder="例如：print、变量、循环"><button type="submit">搜索</button></div></form>
    <p v-if="error" class="notice" role="alert">{{ error }}</p>
    <p v-else-if="searched && !results.length" class="empty-state">没有匹配内容。可以换一个知识点或课时标题再试。</p>
    <ol v-else class="results"><li v-for="result in results" :key="`${result.source_type}-${result.lesson_id}-${result.anchor}`"><a :href="resultLink(result)"><span class="result-meta">{{ result.language }} · {{ result.source_type }}</span><strong>{{ result.title }}</strong><span class="result-snippet">{{ result.snippet }}</span></a></li></ol>
  </section>
</template>

<style scoped>
.search-page { display: grid; gap: var(--hard-space-5); max-width: 70rem; margin: 0 auto; } header p { margin: 0; color: var(--hard-color-primary-strong); } h1 { margin: var(--hard-space-1) 0 0; font-size: clamp(2rem, 5vw, 3.5rem); }
.search-form { display: grid; gap: var(--hard-space-2); padding: var(--hard-space-4); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); color: var(--hard-color-muted); } .search-form div { display: flex; gap: var(--hard-space-2); } input { min-width: 0; flex: 1; min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-space); font: inherit; } button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-4); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; cursor: pointer; }
.results { display: grid; gap: var(--hard-space-2); padding: 0; margin: 0; list-style: none; } .results a { display: grid; gap: var(--hard-space-1); padding: var(--hard-space-4); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); color: var(--hard-color-text); background: var(--hard-color-surface); text-decoration: none; } .results a:hover { border-color: var(--hard-color-primary); } .result-meta { color: var(--hard-color-primary-strong); font-size: var(--hard-text-xs); text-transform: uppercase; } .result-snippet { color: var(--hard-color-muted); white-space: pre-wrap; } .empty-state, .notice { margin: 0; padding: var(--hard-space-4); border-radius: var(--hard-radius-sm); color: var(--hard-color-muted); background: var(--hard-color-surface); } .notice { color: var(--hard-color-danger); }
@media (max-width: 35rem) { .search-form div { flex-direction: column; } }
</style>
