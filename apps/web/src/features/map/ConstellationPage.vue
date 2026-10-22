<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";
import HomeConstellations from "./HomeConstellations.vue";
import LessonProgress from "./LessonProgress.vue";
import { refreshMapSnapshot, useMapStore } from "./map.store";
import { useRoute } from "vue-router";
import { requestJson } from "../../api/client";
import { chainLanguages, chainLabels, linkedLanguages, starPositions, type ChainLanguage, type ChainCourse, type ChainConcept } from "./constellation";

const props = defineProps<{ home?: boolean }>();
const snapshot = useMapStore();
const route = useRoute();
const showModules = ref(!!route.query.language);
const motionPaused = ref(false);
const moduleToolbar = ref<HTMLElement>();
async function openCourse(value: ChainLanguage) {
  chooseLanguage(value); showModules.value = true;
  await nextTick();
  moduleToolbar.value?.scrollIntoView?.({ block: "start", behavior: "instant" });
  moduleToolbar.value?.focus({ preventScroll: true });
}
const courses = ref<ChainCourse[]>([]);
const concepts = ref<ChainConcept[]>([]);
const loading = ref(true);
const error = ref("");
const language = ref<ChainLanguage>(chainLanguages.includes(route.query.language as ChainLanguage) ? route.query.language as ChainLanguage : "python");
const moduleId = ref("");
const lessonId = ref("");
const conceptId = ref(props.home ? "functions" : "variables");
const query = ref("");
const modules = computed(() => courses.value.find(course => course.language === language.value)?.modules ?? []);
const activeModule = computed(() => modules.value.find(module => module.id === moduleId.value) ?? modules.value[0]);
const stars = computed(() => starPositions(activeModule.value?.lessons ?? []));
const chainHeight = computed(() => Math.max(260, ...stars.value.map(star => star.y + 100)));
const chainPath = computed(() => stars.value.reduce((path, star, index, all) => {
  if (!index) return `M${star.x} ${star.y}`;
  const previous = all[index - 1];
  if (previous.x === star.x) {
    const curve = star.x + (star.x > 480 ? 65 : -65);
    return `${path} C${curve} ${previous.y + 45} ${curve} ${star.y - 45} ${star.x} ${star.y}`;
  }
  const midpoint = (previous.x + star.x) / 2;
  return `${path} C${midpoint} ${previous.y} ${midpoint} ${star.y} ${star.x} ${star.y}`;
}, ""));
const selected = computed(() => concepts.value.find(concept => concept.id === conceptId.value));
const connected = computed(() => selected.value ? linkedLanguages(selected.value, courses.value) : []);
const matchingConcepts = computed(() => concepts.value.filter(concept =>
  `${concept.name} ${concept.id}`.toLowerCase().includes(query.value.trim().toLowerCase())));
const lessonConcepts = computed(() => concepts.value.filter(concept => concept.slots[language.value]?.status === "available" && concept.slots[language.value].lesson_id === lessonId.value));
const selectedLesson = computed(() => activeModule.value?.lessons.find(lesson => lesson.id === lessonId.value));
const bridgePositions = [{ x: 180, y: 100 }, { x: 780, y: 100 }, { x: 180, y: 320 }, { x: 780, y: 320 }];

function alignWithConcept() {
  const id = selected.value?.slots[language.value]?.lesson_id;
  const module = modules.value.find(item => item.lessons.some(lesson => lesson.id === id));
  moduleId.value = module?.id ?? modules.value[0]?.id ?? "";
  lessonId.value = module ? id! : "";
}
function chooseLanguage(value: ChainLanguage) { language.value = value; alignWithConcept(); }
function chooseConcept(id: string, sourceLanguage?: ChainLanguage) { if (sourceLanguage) language.value = sourceLanguage; conceptId.value = id; alignWithConcept(); }
function chooseModule(id: string) { moduleId.value = id; lessonId.value = ""; conceptId.value = ""; }
function chooseLesson(id: string) {
  lessonId.value = id;
  const match = concepts.value.find(concept => concept.slots[language.value]?.status === "available" && concept.slots[language.value].lesson_id === id);
  conceptId.value = match?.id ?? "";
}
async function load() {
  loading.value = true; error.value = "";
  try {
    const [catalog, comparison] = await Promise.all([
      requestJson<{ courses: ChainCourse[] }>("/api/content/catalog"),
      requestJson<{ concepts: ChainConcept[] }>("/api/compare/concepts"),
    ]);
    courses.value = catalog.courses; concepts.value = comparison.concepts;
    if (!concepts.value.some(concept => concept.id === conceptId.value)) conceptId.value = concepts.value[0]?.id ?? "";
    alignWithConcept();
  } catch { error.value = "星链数据暂时无法读取，请重试。"; }
  finally { loading.value = false; }
}
onMounted(() => { void load(); if (!props.home) void refreshMapSnapshot(); });
</script>

<template>
  <section class="constellation-page" :class="{ 'is-home': home, 'motion-paused': motionPaused }" :aria-labelledby="home ? undefined : 'constellation-title'">
    <header v-if="!home" class="constellation-hero"><div><p class="eyebrow">KNOWLEDGE CONSTELLATIONS</p><h1 id="constellation-title">知识相连，理解更深</h1><p>沿着星链学习，在不同语言之间发现同一个想法。</p></div><span class="constellation-label">知识星链</span></header>
    <p v-if="loading" class="chain-state" role="status">正在连接课程与知识点…</p>
    <div v-else-if="error" class="chain-state" role="alert"><p>{{ error }}</p><button @click="load">重新连接</button></div>
    <template v-else>
      <HomeConstellations v-if="home" v-model:paused="motionPaused" :courses="courses" :concepts="concepts" :selected="selected" @concept="chooseConcept" @course="openCourse" />
      <button v-if="home" class="module-disclosure" :aria-expanded="showModules" @click="showModules = !showModules">{{ showModules ? "收起模块星链" : "查看模块星链" }}</button>
      <div v-if="!home || showModules" ref="moduleToolbar" tabindex="-1" class="chain-toolbar"><nav aria-label="星链语言"><button v-for="lang in chainLanguages" :key="lang" :aria-pressed="language === lang" @click="chooseLanguage(lang)">{{ chainLabels[lang] }}</button></nav><RouterLink :to="`/course/${language}`">打开课程目录</RouterLink></div>
      <div v-if="!home || showModules" class="chain-layout">
        <nav class="module-selector" aria-label="课程星链"><p class="eyebrow">{{ modules.length }} 组模块星链</p><button v-for="(module, index) in modules" :key="module.id" :aria-pressed="activeModule?.id === module.id" @click="chooseModule(module.id)"><span>{{ String(index + 1).padStart(2, '0') }}</span><strong>{{ module.title }}</strong><small>{{ module.lessons.length }} 星点</small></button></nav>
        <section class="chain-panel" :aria-label="`${activeModule?.title ?? '课程'}星链`">
          <header><div><p class="eyebrow">{{ chainLabels[language] }} · 模块星链</p><h2>{{ activeModule?.title ?? '暂无模块' }}</h2></div><div class="chain-panel-tools"><span>{{ stars.length }} 个课时知识点</span><button class="chain-motion-toggle" :aria-pressed="motionPaused" @click="motionPaused = !motionPaused">{{ motionPaused ? '开启星链动效' : '暂停星链动效' }}</button></div></header>
          <p class="chain-hint">星点按课时目录顺序相连。选择一个星点，查看它的跨语言联系。</p>
          <div :key="activeModule?.id" class="star-canvas" :style="{ height: `${chainHeight}px` }">
            <svg :viewBox="`0 0 960 ${chainHeight}`" preserveAspectRatio="none" aria-hidden="true"><path :d="chainPath" class="chain-track" fill="none" /><path :d="chainPath" class="chain-flow" fill="none" /></svg>
            <button v-for="(star,index) in stars" :key="star.id" class="star-node" :class="{ 'is-selected': lessonId === star.id }" :style="{ left: `${star.x / 960 * 100}%`, top: `${star.y}px`, '--star-delay': `${Math.min(index, 8) * 35}ms` }" :aria-pressed="lessonId === star.id" @click="chooseLesson(star.id)"><span class="star-light" aria-hidden="true"></span><strong>{{ star.title }}</strong><LessonProgress :lesson-id="star.id" /></button>
          </div>
          <ol class="mobile-star-chain"><li v-for="star in stars" :key="star.id"><button :aria-pressed="lessonId === star.id" @click="chooseLesson(star.id)"><span class="star-light" aria-hidden="true"></span>{{ star.title }}<LessonProgress :lesson-id="star.id" /></button></li></ol>
          <div v-if="selectedLesson" class="selected-lesson"><strong>{{ selectedLesson.title }}</strong><LessonProgress :lesson-id="selectedLesson.id" /><RouterLink :to="`/lesson/${selectedLesson.id}`">阅读课时</RouterLink><RouterLink :to="`/assessment/${selectedLesson.id}`">进入练习</RouterLink><RouterLink v-if="snapshot.lessons[selectedLesson.id]?.status === 'due_review'" to="/review">去复习</RouterLink><div v-if="lessonConcepts.length" class="concept-chips"><button v-for="concept in lessonConcepts" :key="concept.id" :aria-pressed="conceptId === concept.id" @click="conceptId = concept.id">{{ concept.name }}</button></div><p v-else>本课尚无已标注的跨语言对照，仍可正常学习。</p></div>
        </section>
      </div>
      <section class="resonance" aria-labelledby="resonance-title">
        <header><div><p class="eyebrow">CROSS-LANGUAGE CONNECTIONS</p><h2 id="resonance-title">跨语言共鸣</h2><p>相同概念连接不同星链；连线仅代表已收录的概念对照。</p></div><label>查找相似知识点<input v-model="query" type="search" placeholder="例如：变量、循环、指针" aria-label="查找星链概念"></label></header>
        <label v-if="home" class="home-concept-select">切换共同概念<select aria-label="切换共同概念" :value="conceptId" @change="chooseConcept(($event.target as HTMLSelectElement).value)"><option value="" disabled>请选择知识点</option><option v-for="concept in matchingConcepts" :key="concept.id" :value="concept.id">{{ concept.name }}</option></select></label>
        <div v-else class="concept-chips" aria-label="选择对照概念"><button v-for="concept in matchingConcepts" :key="concept.id" :aria-pressed="conceptId === concept.id" @click="chooseConcept(concept.id)">{{ concept.name }}</button></div>
        <p v-if="!matchingConcepts.length" role="status">没有匹配的概念，请换一个关键词。</p>
        <template v-if="selected">
          <div v-if="!home" class="resonance-visual" :aria-label="`${selected.name}跨语言连线`">
            <svg viewBox="0 0 960 420" preserveAspectRatio="none" aria-hidden="true"><template v-for="(lang, index) in chainLanguages" :key="lang"><path v-if="connected.includes(lang)" :d="`M480 210 Q${bridgePositions[index].x} 210 ${bridgePositions[index].x} ${bridgePositions[index].y}`" fill="none" :data-connection="lang" /></template></svg>
            <div class="concept-center"><small>共同概念</small><strong>{{ selected.name }}</strong><span>{{ connected.length }} 条语言连接</span></div>
            <button v-for="(lang, index) in chainLanguages" :key="lang" class="language-star" :class="{ 'is-missing': !connected.includes(lang) }" :style="{ left: `${bridgePositions[index].x / 960 * 100}%`, top: `${bridgePositions[index].y / 420 * 100}%` }" :disabled="!connected.includes(lang)" @click="chooseLanguage(lang)"><span class="star-light" aria-hidden="true"></span><strong>{{ chainLabels[lang] }}</strong><small>{{ connected.includes(lang) ? selected.slots[lang].lesson_title : '暂无对应课时' }}</small></button>
          </div>
          <div class="common-ground" aria-live="polite"><span>相同处</span><h3>{{ selected.name }}</h3><p>{{ selected.description }}</p></div>
          <div class="connection-details"><article v-for="lang in chainLanguages" :key="lang" :data-connection-detail="lang"><h3>{{ chainLabels[lang] }}</h3><template v-if="connected.includes(lang)"><LessonProgress :lesson-id="selected.slots[lang].lesson_id" /><p>{{ selected.slots[lang].summary }}</p><h4>不同处与使用边界</h4><p>{{ selected.slots[lang].difference || '当前未补充额外差异说明。' }}</p><pre v-if="selected.slots[lang].code"><code>{{ selected.slots[lang].code }}</code></pre><RouterLink :to="`/lesson/${selected.slots[lang].lesson_id}`">{{ selected.slots[lang].lesson_title }} · 阅读课时</RouterLink></template><p v-else>暂无对应课时。{{ selected.slots[lang]?.note }}</p></article></div>
        </template>
        <p v-else class="chain-state">选择一个已标注概念，查看相同处、不同处与课程连接。</p>
      </section>
    </template>
  </section>
</template>

<style scoped>
.constellation-page { max-width: 88rem; margin: auto; display: grid; gap: 2rem; }
.constellation-hero { display: flex; justify-content: space-between; align-items: center; gap: 2rem; padding: 2.5rem; border: 1px solid var(--hard-color-line); border-radius: 1.5rem; background: linear-gradient(90deg, #080d1bcc, #080d1b55), url('/art/knowledge-nebula.png') center / cover; }
.eyebrow { color: var(--hard-color-primary-strong); font-size: .75rem; letter-spacing: .1em; margin: 0 0 .5rem; }
h1 { font-size: clamp(2rem, 3.4vw, 3.2rem); line-height: 1.2; letter-spacing: -.04em; margin: 0 0 1rem; } h2 { margin: 0; font-size: 1.5rem; } h3 { margin: 0 0 .75rem; } p { color: var(--hard-color-muted); line-height: 1.75; }
.constellation-label { white-space: nowrap; color: var(--hard-color-cyan); border: 1px solid var(--hard-color-line); border-radius: 999px; padding: .75rem 1rem; }
button { cursor: pointer; min-height: 44px; color: var(--hard-color-text); font: inherit; border: 1px solid var(--hard-color-line); border-radius: .75rem; background: var(--hard-color-surface); }
button[aria-pressed='true'] { border-color: var(--hard-color-primary-strong); color: var(--hard-color-primary-strong); background: var(--hard-color-surface-raised); }
a { color: var(--hard-color-primary-strong); text-underline-offset: .3em; }
.chain-toolbar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem; } .chain-toolbar nav { display: flex; gap: .5rem; } .chain-toolbar button { padding: .5rem 1.25rem; border-radius: 999px; }
.chain-layout { display: grid; grid-template-columns: 16rem minmax(0, 1fr); gap: 1.5rem; align-items: start; }
.module-selector { display: grid; gap: .5rem; } .module-selector button { display: grid; grid-template-columns: 1.5rem 1fr; gap: .2rem .75rem; padding: 1rem; text-align: left; } .module-selector strong { font-size: .85rem; font-weight: 500; } .module-selector small { grid-column: 2; color: var(--hard-color-muted); } .module-selector button > span { grid-row: span 2; color: var(--hard-color-muted); font-size: .75rem; }
.chain-panel { min-width: 0; overflow: hidden; border: 1px solid var(--hard-color-line); border-radius: 1.25rem; background: var(--hard-color-surface); } .chain-panel > header { display: flex; align-items: start; justify-content: space-between; gap: 1rem; padding: 1.5rem 1.5rem .5rem; } .chain-panel header > span { color: var(--hard-color-muted); font-size: .75rem; white-space: nowrap; } .chain-hint { margin: 0; padding: .5rem 1.5rem; font-size: .8rem; }
.star-canvas { position: relative; background: linear-gradient(#080d1b44,#080d1bbb),url('/art/knowledge-nebula.png') center / cover; } svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; } polyline, path { stroke: #9e8ce0; stroke-width: 1.3; vector-effect: non-scaling-stroke; opacity: .6; }
.star-node { position: absolute; transform: translate(-50%, -20px); display: grid; justify-items: center; gap: .6rem; width: 23%; padding: .35rem; border: 0; background: transparent; text-align: center; } .star-node strong { max-width: 100%; padding: .25rem .5rem; border-radius: .4rem; background: #080d1bdf; font-size: .8rem; line-height: 1.5; font-weight: 500; } .star-light { display: block; width: .65rem; height: .65rem; border-radius: 50%; background: var(--hard-color-cyan); box-shadow: 0 0 0 5px #4de5e714, 0 0 20px #4de5e766; } .star-node.is-selected .star-light { background: #cfbfff; box-shadow: 0 0 0 8px #ad8bff25, 0 0 28px #ad8bff; } .star-node[aria-pressed='true'] { background: transparent; }
.selected-lesson { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem; padding: 1.5rem; border-top: 1px solid var(--hard-color-line); } .selected-lesson p { margin: 0; width: 100%; font-size: .85rem; } .mobile-star-chain { display: none; }
.resonance { display: grid; gap: 1.5rem; } .resonance > header { display: flex; justify-content: space-between; align-items: end; gap: 2rem; } .resonance header p { margin-bottom: 0; } label { display: grid; gap: .5rem; color: var(--hard-color-muted); font-size: .85rem; } input { min-height: 46px; width: 20rem; max-width: 100%; padding: .75rem 1rem; color: var(--hard-color-text); background: var(--hard-color-surface); border: 1px solid var(--hard-color-line); border-radius: .75rem; font: inherit; }
.concept-chips { display: flex; flex-wrap: wrap; gap: .5rem; } .concept-chips button { padding: .45rem .9rem; border-radius: 999px; font-size: .8rem; }
.resonance-visual { position: relative; height: 420px; border: 1px solid var(--hard-color-line); border-radius: 1.25rem; background: linear-gradient(#080d1b44,#080d1b55),url('/art/knowledge-nebula.png') center / cover; }
.concept-center { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%); width: 10rem; height: 10rem; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: .6rem; border-radius: 50%; border: 1px solid #bdaaff; background: #171931f5; box-shadow: 0 0 55px #8a5cff38; } .concept-center strong { font-size: 1.5rem; } .concept-center small,.concept-center span { font-size: .75rem; color: var(--hard-color-muted); }
.language-star { position: absolute; transform: translate(-50%,-50%); display: grid; justify-items: center; gap: .6rem; width: 24%; padding: 1rem; background: #0d1528f0; } .language-star strong { font-size: 1.1rem; } .language-star small { font-size: .75rem; color: var(--hard-color-muted); } .language-star.is-missing { opacity: .55; border-style: dashed; cursor: default; } .language-star.is-missing .star-light { box-shadow: none; background: var(--hard-color-muted); }
.common-ground { padding: 1.5rem 2rem; border-left: 3px solid var(--hard-color-cyan); background: var(--hard-color-surface); border-radius: .5rem; } .common-ground > span { color: var(--hard-color-cyan); font-size: .8rem; } .common-ground h3 { margin: .5rem 0; } .common-ground p { margin: 0; }
.connection-details { display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: 1rem; } .connection-details article { padding: 1.5rem; min-width: 0; border: 1px solid var(--hard-color-line); border-radius: 1rem; background: var(--hard-color-surface); } .connection-details h3 { color: var(--hard-color-cyan); } .connection-details h4 { margin-bottom: .4rem; font-size: .8rem; } .connection-details p,.connection-details a { font-size: .85rem; } pre { padding: .8rem; border-radius: .5rem; background: var(--hard-color-space); overflow: auto; font-size: .75rem; } .chain-state { padding: 2rem; border: 1px solid var(--hard-color-line); border-radius: 1rem; }
@media (min-width: 65.01rem) { .module-selector { max-height: 34rem; overflow-y: auto; padding-right: .5rem; scrollbar-width: thin; } }
@media (max-width: 65rem) { .chain-layout { grid-template-columns: 1fr; } .module-selector { display: flex; overflow-x: auto; padding-bottom: .5rem; scrollbar-width: thin; } .module-selector > p { display: none; } .module-selector button { flex: 0 0 13rem; } .connection-details { grid-template-columns: repeat(2,minmax(0,1fr)); } }
@media (max-width: 42rem) { .constellation-hero { padding: 1.5rem; } .constellation-label { display: none; } .chain-toolbar button { padding: .5rem 1rem; } .chain-panel > header, .resonance > header { flex-direction: column; align-items: start; } .resonance label,input { width: 100%; } .star-canvas { display: none; } .mobile-star-chain { display: grid; list-style: none; padding: 1rem 1.5rem; margin: 0; } .mobile-star-chain li { border-left: 1px solid var(--hard-color-line); padding: .15rem 0 .15rem 1rem; } .mobile-star-chain button { display: flex; align-items: center; gap: 1rem; width: 100%; padding: .75rem; text-align: left; font-size: .9rem; } .mobile-star-chain .star-light { flex-shrink: 0; } .resonance-visual { height: 370px; } .concept-center { width: 6rem; height: 6rem; } .concept-center strong { font-size: 1rem; } .concept-center span { display: none; } .language-star { width: 34%; padding: .7rem; } .language-star small { font-size: .65rem; } .connection-details { grid-template-columns: 1fr; } .common-ground { padding: 1.25rem; } }
.is-home {width:100%;max-width:100%;gap:1.5rem;}
.module-disclosure {justify-self:center;padding:.6rem 1.5rem;background:transparent;border-color:#39465c;color:#b3c1d7;font-size:.82rem;}
.is-home .resonance {margin-top:1rem;padding:2rem 0;border-top:1px solid #ffffff14;gap:1.75rem;}
.is-home .resonance>header p {font-size:.88rem;}.is-home .resonance h2 {font-size:1.5rem;font-weight:550;}
.is-home .common-ground {border-left:2px solid #94d4ca;padding:1.1rem 1.5rem;background:#121c25;border-radius:0 8px 8px 0;}
.is-home .connection-details {gap:0;border:1px solid #ffffff12;border-radius:12px;overflow:hidden;background:#10151d;}
.is-home .connection-details article {background:transparent;border:0;border-left:1px solid #ffffff10;border-radius:0;padding:1.5rem;}
.is-home .connection-details article:first-child {border-left:0;}.is-home .connection-details h3 {font-size:1rem;color:#e3e9f3;font-weight:550;}
.is-home .connection-details p {font-size:.88rem;line-height:1.9;color:#aab7cb;}.is-home .connection-details h4 {font-size:.75rem;color:#d3dce9;font-weight:500;margin-top:1.3rem;}
.is-home .connection-details pre {background:#090e16;padding:1rem;font-size:.72rem;border:1px solid #ffffff08;}
.home-concept-select {display:flex;align-items:center;gap:1rem;font-size:.8rem;}
select {min-height:44px;padding:.5rem 1rem;color:#dce7f8;background:#101824;border:1px solid #35435a;border-radius:7px;font:inherit;}
.chain-panel {background:#10151d;}.star-canvas {background:linear-gradient(#0c121ae8,#0c121ae8),url('/art/knowledge-nebula.png') center / cover;}
@media(max-width:52rem) {.is-home .resonance {padding:1.5rem 0;}.is-home .connection-details article {padding:1.25rem;}.is-home .connection-details {grid-template-columns:1fr;}.is-home .connection-details article {border-left:0;border-top:1px solid #ffffff10;}.is-home .connection-details article:first-child {border-top:0;}}
/* The curve follows catalog order; it does not imply authored prerequisites. */
.chain-panel-tools {display:grid;justify-items:end;gap:.6rem;flex:none;}
.chain-panel-tools>span {color:var(--hard-color-muted);font-size:.72rem;}
.chain-motion-toggle {min-height:36px;padding:.35rem .65rem;border-radius:7px;font-size:.7rem;background:#1a2636;}
.chain-panel {border-color:#3a4961;box-shadow:0 15px 40px #00000018;}
.star-canvas {background:linear-gradient(#0b142370,#0b1423b8),url('/art/knowledge-nebula.png') center / cover;}
.star-canvas .chain-track {stroke:#8cacc9;stroke-width:1;opacity:.5;}
.star-canvas .chain-flow {stroke:#c9d9ff;stroke-width:1.8;stroke-dasharray:14 170;opacity:.85;animation:chain-travel 8s linear infinite;}
.star-node {width:22%;gap:.55rem;transform:translate(-50%,-10px);animation:star-arrive 400ms both;animation-delay:var(--star-delay,0ms);}
.star-node strong {padding:.4rem .6rem;border:1px solid #778ba526;background:#101b2ad9;border-radius:8px;color:#dce6f5;}
.star-node .star-light {width:.5rem;height:.5rem;box-shadow:0 0 0 4px #a8dccc12,0 0 13px #a8dccc50;animation:star-breathe 4s ease-in-out infinite;}
.star-node.is-selected strong {border-color:#aebcf790;background:#22314a;color:#fff;}
.star-node.is-selected .star-light {background:#c4baff;box-shadow:0 0 0 5px #b6a9ec26,0 0 16px #a8a1e480;}
.star-node:hover strong {border-color:#aebcf780;}
.module-selector button {border-color:transparent;background:transparent;}
.module-selector button:hover {background:#ffffff05;border-color:#ffffff15;}
.module-selector button[aria-pressed='true'] {background:#1d2a3d;border-color:#8fa3d075;color:#e0e8fb;}
.selected-lesson {background:#152133;}
.mobile-star-chain li {position:relative;border-left:1px solid #556b8d;padding-left:1.1rem;}
.mobile-star-chain .star-light {position:absolute;left:-4px;top:1.1rem;width:7px;height:7px;}
.motion-paused :deep(*),.motion-paused :deep(*::before),.motion-paused :deep(*::after) {animation-play-state:paused!important;}
.motion-paused .star-node {animation:none;opacity:1;translate:none;}
@keyframes chain-travel {to {stroke-dashoffset:-368;}}
@keyframes star-breathe {0%,100% {opacity:.65;}50% {opacity:1;}}
@keyframes star-arrive {from {opacity:0;translate:0 5px;}to {opacity:1;translate:0 0;}}
@media(max-width:52rem) {.chain-panel-tools {gap:.3rem;}.chain-motion-toggle {font-size:.65rem;}.chain-panel>header {padding:1.2rem 1rem .5rem;}.chain-panel h2 {font-size:1.15rem;}.selected-lesson {padding:1rem;}.resonance>header {gap:1rem;}}
</style>
