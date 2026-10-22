<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";

import { requestJson } from "../../api/client";

interface SearchResult { source_type: string; language: string; lesson_id: string; title: string; snippet: string; anchor: string; }

const query = ref("");
const results = ref<SearchResult[]>([]);
const searched = ref(false);
const error = ref("");
const searching = ref(false);
const submittedQuery = ref("");
const languageLabels: Record<string, string> = { python: "Python", java: "Java", csharp: "C#", cpp: "C++" };
const sourceLabels: Record<string, string> = { lesson: "课程课时", concept: "知识概念", note: "学习笔记", bookmark: "收藏" };
let searchVersion = 0;

async function search() {
  const version = ++searchVersion;
  searched.value = true;
  error.value = "";
  results.value = [];
  submittedQuery.value = query.value.trim();
  if (!submittedQuery.value) { searching.value = false; return; }
  searching.value = true;
  try {
    const response = await requestJson<{ results: SearchResult[] }>(`/api/search?q=${encodeURIComponent(query.value.trim())}`);
    if (version === searchVersion) results.value = response.results;
  } catch { if (version === searchVersion) error.value = "搜索暂时不可用，请稍后重试。"; }
  finally { if (version === searchVersion) searching.value = false; }
}

function resultLink(result: SearchResult) {
  return `/lesson/${result.lesson_id}${result.anchor ? `#${encodeURIComponent(result.anchor)}` : ""}`;
}
</script>

<template>
  <section class="search-page" aria-labelledby="search-title">
    <header><p>找到知识，也找到新的连接</p><h1 id="search-title">全文搜索</h1><p class="page-intro">搜索课程、知识点、笔记与收藏，回到问题发生的地方。</p></header>
    <form class="search-form" role="search" @submit.prevent="search"><label for="search-query">搜索课程内容</label><div><input id="search-query" v-model="query" aria-label="搜索课程内容" type="search" autocomplete="off" placeholder="试试：变量、循环、print"><button type="submit">搜索 <span aria-hidden="true">↗</span></button></div><span class="search-hint">支持中文知识点与代码关键词 · 按 Enter 搜索</span></form>
    <div v-if="!searched" class="search-discover"><span class="discover-symbol" aria-hidden="true">✧</span><h2>从一个问题开始探索</h2><p>记得一个关键词，就能重新找到那一课。</p><div><button v-for="term in ['变量', '循环', '函数']" :key="term" type="button" @click="query = term; search()">{{ term }} <span aria-hidden="true">↗</span></button></div><RouterLink to="/constellations">探索知识星链，连接不同语言的同一概念 →</RouterLink></div>
    <p v-if="searching" class="empty-state" role="status">正在查找相关内容…</p>
    <p v-else-if="error" class="notice" role="alert">{{ error }}</p>
    <div v-else-if="searched && !submittedQuery" class="empty-state" role="status"><h2>请输入关键词</h2><p>可以从一个知识点、课时标题或代码关键词开始。</p></div>
    <div v-else-if="searched && !results.length" class="empty-state" role="status"><h2>没有找到“{{ submittedQuery }}”</h2><p>没有匹配内容。可以换一个知识点或课时标题再试。</p><RouterLink to="/course/python">浏览课程 →</RouterLink></div>
    <template v-else-if="results.length"><div class="results-heading" data-search-summary role="status"><h2>“{{ submittedQuery }}”的搜索结果</h2><span>{{ results.length }} 条相关内容</span></div><ol class="results"><li v-for="(result, index) in results" :key="`${result.source_type}-${result.lesson_id}-${result.anchor}-${index}`"><a :href="resultLink(result)"><span class="result-meta"><span>{{ languageLabels[result.language] ?? result.language }}</span> · {{ sourceLabels[result.source_type] ?? result.source_type }}</span><strong>{{ result.title }} <span aria-hidden="true">↗</span></strong><span class="result-snippet">{{ result.snippet }}</span><span class="result-action">打开所在课时 →</span></a></li></ol></template>
  </section>
</template>

<style scoped>
.search-page { display: grid; gap: var(--hard-space-5); max-width: 70rem; margin: 0 auto; } header p { margin: 0; color: var(--hard-color-primary-strong); } h1 { margin: var(--hard-space-1) 0 0; font-size: clamp(2rem, 5vw, 3.5rem); }
.search-form { display: grid; gap: var(--hard-space-2); padding: var(--hard-space-4); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); color: var(--hard-color-muted); } .search-form div { display: flex; gap: var(--hard-space-2); } input { min-width: 0; flex: 1; min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-space); font: inherit; } button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-4); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; cursor: pointer; }
.results { display: grid; gap: var(--hard-space-2); padding: 0; margin: 0; list-style: none; } .results a { display: grid; gap: var(--hard-space-1); padding: var(--hard-space-4); border: .0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); color: var(--hard-color-text); background: var(--hard-color-surface); text-decoration: none; } .results a:hover { border-color: var(--hard-color-primary); } .result-meta { color: var(--hard-color-primary-strong); font-size: var(--hard-text-xs); text-transform: uppercase; } .result-snippet { color: var(--hard-color-muted); white-space: pre-wrap; } .empty-state, .notice { margin: 0; padding: var(--hard-space-4); border-radius: var(--hard-radius-sm); color: var(--hard-color-muted); background: var(--hard-color-surface); } .notice { color: var(--hard-color-danger); }
@media (max-width: 35rem) { .search-form div { flex-direction: column; } }
.search-discover { padding: 2rem; border: 1px solid var(--hard-color-line); border-radius: 1rem; background: var(--hard-color-surface); }
.search-discover h2 { margin: 0; font-size: 1.25rem; } .search-discover p { color: var(--hard-color-muted); }
.search-discover > div { display: flex; flex-wrap: wrap; gap: .75rem; margin-bottom: 1.5rem; }
.search-discover button { background: var(--hard-color-surface-raised); border: 1px solid var(--hard-color-line); border-radius: 999px; }
.search-discover a { color: var(--hard-color-primary-strong); font-size: .875rem; }
.page-intro { margin-top: .85rem; color: var(--hard-color-muted); line-height: 1.8; }
.search-form { padding: 1.5rem; gap: .85rem; border-color: color-mix(in srgb, var(--hard-color-primary) 40%, var(--hard-color-line)); background: linear-gradient(120deg, color-mix(in srgb, var(--hard-color-primary) 7%, var(--hard-color-surface)), var(--hard-color-surface)); }
.search-form input { min-height: 3.25rem; }
.search-form button { min-width: 7rem; }
.search-hint { color: var(--hard-color-muted); font-size: .75rem; }
.search-discover { position: relative; padding: clamp(1.5rem, 4vw, 2.5rem); background: transparent; border-style: dashed; }
.discover-symbol { display: block; margin-bottom: 1.25rem; color: var(--hard-color-cyan); font-size: 2rem; }
.search-discover p { line-height: 1.8; }
.search-discover button { display: inline-flex; align-items: center; gap: 1rem; }
.search-discover button span { color: var(--hard-color-muted); }
.results-heading { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: .75rem; }
.results-heading h2, .empty-state h2 { margin: 0; font-size: 1.1rem; }
.results-heading > span { color: var(--hard-color-muted); font-size: .8rem; }
.results { gap: 0; border-top: 1px solid var(--hard-color-line); }
.results a { padding: 1.5rem .5rem; gap: .7rem; border: 0; border-bottom: 1px solid var(--hard-color-line); border-radius: 0; background: transparent; transition: background 180ms ease; }
.results a:hover { background: color-mix(in srgb, var(--hard-color-primary) 5%, transparent); }
.results strong { display: flex; justify-content: space-between; gap: 1rem; font-size: 1.125rem; }
.results strong > span, .result-action { color: var(--hard-color-cyan); font-size: .8rem; }
.result-meta { text-transform: none; letter-spacing: .03em; }
.result-meta > span { color: var(--hard-color-cyan); }
.result-snippet { max-width: 65rem; line-height: 1.85; overflow-wrap: anywhere; }
.empty-state { padding: 2rem; border: 1px dashed var(--hard-color-line); background: transparent; line-height: 1.8; }
.empty-state a { color: var(--hard-color-primary-strong); }
</style>
