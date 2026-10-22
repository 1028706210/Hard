<script setup lang="ts">
import { computed } from "vue";
import { useMapStore } from "./map.store";
import LessonProgress from "./LessonProgress.vue";
import { chainLanguages, chainLabels, linkedLanguages, groupedConcepts, type ChainConcept, type ChainCourse, type ChainLanguage } from "./constellation";
const props = defineProps<{ courses: ChainCourse[]; concepts: ChainConcept[]; selected?: ChainConcept }>();
const emit = defineEmits<{ concept: [id: string, language: ChainLanguage]; course: [language: ChainLanguage] }>();
const paused = defineModel<boolean>("paused", { default: false });
const snapshot = useMapStore();
const icons = { python: "python", java: "java", csharp: "csharp", cpp: "cplusplus" };
const accents = ["#c0aaed", "#e7c883", "#8fd5c8", "#9abfea"];
const groups = computed(() => groupedConcepts(props.concepts, props.selected?.id));
const positions = [
  [{ x: 182, y: 49 }, { x: 290, y: 74 }, { x: 410, y: 46 }],
  [{ x: 168, y: 157 }, { x: 287, y: 178 }, { x: 415, y: 149 }],
  [{ x: 189, y: 263 }, { x: 304, y: 281 }, { x: 418, y: 254 }],
];
const nodes = computed(() => groups.value.flatMap((group, row) => group.displayed.map((concept, index) => ({ concept, group: group.id, ...positions[row][index] }))));
const connected = computed(() => props.selected ? linkedLanguages(props.selected, props.courses) : []);
const available = (concept: ChainConcept, language: ChainLanguage) => linkedLanguages(concept, props.courses).includes(language);
function localEdges(language: ChainLanguage) {
  const mapped = nodes.value.filter(node => available(node.concept, language));
  return mapped.flatMap((node, index) => {
    const previous = mapped[index - 1];
    if (!previous || previous.group !== node.group) return [];
    return [{ id: node.concept.id, path: `M${previous.x} ${previous.y} Q${(previous.x + node.x) / 2} ${Math.min(previous.y, node.y) - 16} ${node.x} ${node.y}` }];
  });
}
function bridgePath(index: number) {
  const node = nodes.value.find(item => item.concept.id === props.selected?.id);
  if (!node) return "";
  const x = (index % 2) * 500 + node.x;
  const y = (index > 1 ? 320 : 0) + node.y;
  return `M500 320 C${index % 2 ? 650 : 350} 320 ${x} ${y + (index > 1 ? -65 : 65)} ${x} ${y}`;
}
</script>

<template>
  <section class="home-atlas" :class="{ 'motion-paused': paused }" aria-label="课程知识星座">
    <div class="atlas-legend">
      <div><span class="atlas-eyebrow">THE CONNECTED UNIVERSE</span><strong>探索知识的连接</strong></div>
      <p>主题内知识链 <span aria-hidden="true">·</span> 当前概念的跨语言关联</p>
      <button class="motion-toggle" :aria-pressed="paused" @click="paused = !paused"><span aria-hidden="true">{{ paused ? '▶' : 'Ⅱ' }}</span>{{ paused ? '开启星空动效' : '暂停星空动效' }}</button>
    </div>
    <div class="atlas-scene">
      <div class="drifting-stars" aria-hidden="true"><img :src="'/art/knowledge-clusters.png'" alt="" draggable="false"></div>
      <svg class="semantic-bridges" viewBox="0 0 1000 640" preserveAspectRatio="none" aria-hidden="true"><template v-for="(lang,index) in chainLanguages" :key="lang"><path v-if="connected.includes(lang)" :d="bridgePath(index)" class="bridge-base" :data-connection="lang" /><path v-if="connected.includes(lang)" :d="bridgePath(index)" class="bridge-light" /></template></svg>
      <div :key="selected?.id" class="shared-star" aria-live="polite"><span class="shared-kicker">共同的想法</span><strong>{{ selected?.name ?? '共同概念' }} · 跨语言连接</strong><small>{{ connected.length }} 门语言有已标注课时</small></div>
      <section v-for="(lang,index) in chainLanguages" :key="lang" class="language-constellation" :style="{ '--constellation-color': accents[index] }" :data-map-world="lang" :data-route-node="lang" :aria-label="`${chainLabels[lang]}知识星座`">
        <svg class="local-network" viewBox="0 0 500 320" preserveAspectRatio="none" aria-hidden="true"><template v-for="edge in localEdges(lang)" :key="edge.id"><path :d="edge.path" /><path class="route-flow" :d="edge.path" /></template></svg>
        <button class="language-heading" @click="emit('course',lang)"><img :src="`/art/languages/${icons[lang]}.svg`" alt="" width="44" height="44"><strong>{{ chainLabels[lang] }}</strong><small>{{ snapshot.languages[lang].label }}</small><small>展开课程星链 <span aria-hidden="true">↗</span></small></button>
        <div v-for="(group,row) in groups" :key="group.id" class="knowledge-group" :data-knowledge-group="group.id" :style="{ top: `${(row * 105 + 12) / 320 * 100}%` }"><strong>{{ group.title }}</strong><small>{{ group.members.filter(concept => available(concept, lang)).length }}/{{ group.members.length }} 已映射</small></div>
        <button v-for="(node,i) in nodes" :key="node.concept.id" class="concept-star" :class="{ selected: selected?.id === node.concept.id }" :style="{ left: `${node.x / 500 * 100}%`, top: `${node.y / 320 * 100}%`, '--pulse-delay': `${i * -.8 - index}s` }" :disabled="!available(node.concept,lang)" :aria-label="`${chainLabels[lang]} · ${node.concept.name}${available(node.concept,lang) ? '' : '，暂无标注课时'}`" :aria-description="snapshot.lessons[node.concept.slots[lang]?.lesson_id ?? '']?.label" :aria-pressed="selected?.id === node.concept.id" @click="emit('concept',node.concept.id,lang)"><span class="data-star" aria-hidden="true"></span><span>{{ node.concept.name }}</span><LessonProgress v-if="available(node.concept,lang)" :lesson-id="node.concept.slots[lang].lesson_id" /></button>
      </section>
    </div>
    <p class="atlas-caption"><span>四种语言，连接同一个想法。</span>主题连线不代表先修要求；暗色星点暂无标注课时。下方可探索全部概念。</p>
  </section>
</template>

<style scoped>
.home-atlas {position:relative;overflow:hidden;border:1px solid #37465b;border-radius:20px;background:#0d141e;box-shadow:0 20px 70px #00000020;}
.atlas-legend {display:flex;align-items:center;gap:1.5rem;padding:1.15rem 1.6rem;border-bottom:1px solid #ffffff0c;background:#101722;}
.atlas-legend>div {display:grid;gap:.25rem;margin-right:auto;}.atlas-eyebrow {font-size:.58rem;letter-spacing:.2em;color:#91a2bf;}.atlas-legend strong {font-size:1rem;font-weight:550;color:#e5eaf3;letter-spacing:.03em;}
.atlas-legend p {margin:0;color:#9aaac0;font-size:.72rem;}.atlas-legend p span {margin-inline:.6rem;color:#526079;}
.motion-toggle {display:inline-flex;align-items:center;gap:.6rem;min-height:44px;padding:.5rem .8rem;border:1px solid #4b5870;border-radius:8px;background:#172130;color:#c8d4e7;font:inherit;font-size:.73rem;white-space:nowrap;}.motion-toggle:hover {border-color:#9faed0;background:#1e2b3d;}.motion-toggle>span {font-size:.7rem;}
.atlas-scene {position:relative;isolation:isolate;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));height:580px;background:linear-gradient(90deg,#0a101759,transparent 45%,#0a101730);}
.drifting-stars {position:absolute;inset:0;z-index:-1;overflow:hidden;pointer-events:none;opacity:.31;}.drifting-stars img {width:100%;height:100%;object-fit:cover;animation:stardust-drift 28s ease-in-out infinite alternate;}
.semantic-bridges {position:absolute;inset:0;z-index:1;width:100%;height:100%;pointer-events:none;}.bridge-base,.bridge-light {fill:none;vector-effect:non-scaling-stroke;}.bridge-base {stroke:#90b3cc;stroke-width:.85;opacity:.38;}.bridge-light {stroke:#d1e8f4;stroke-width:1.5;stroke-dasharray:16 170;opacity:.85;animation:travel 8s linear infinite;}
.language-constellation {position:relative;height:290px;min-width:0;}.local-network {position:absolute;inset:0;width:100%;height:100%;pointer-events:none;}.local-network path {fill:none;stroke:var(--constellation-color);stroke-width:1;opacity:.4;vector-effect:non-scaling-stroke;}.local-network .route-flow {stroke-width:1.7;stroke-dasharray:8 90;opacity:.8;animation:local-travel 7s linear infinite;}
.language-heading {position:absolute;left:3%;top:32%;z-index:2;display:flex;flex-direction:column;align-items:center;gap:.5rem;width:24%;padding:.7rem .3rem;border:1px solid transparent;border-radius:12px;background:transparent;color:#eef2f8;}.language-heading:hover {border-color:#ffffff16;background:#101b2ab8;}
.language-heading img {width:41px;height:41px;margin-bottom:.25rem;animation:icon-float 7s ease-in-out infinite;}.language-heading strong {font-size:1.55rem;line-height:1.2;font-weight:550;letter-spacing:-.035em;}.language-heading small {font-size:.68rem;color:#a4b2c6;}.language-heading small:last-child {margin-top:.3rem;color:var(--constellation-color);font-size:.65rem;}
.knowledge-group {position:absolute;left:34%;display:flex;align-items:baseline;gap:.65rem;pointer-events:none;}.knowledge-group strong {font-size:.72rem;font-weight:500;color:#acb9cb;}.knowledge-group small {font-size:.58rem;color:#8a9ab0;}
.concept-star {position:absolute;z-index:2;transform:translate(-50%,-9px);display:flex;flex-direction:column;align-items:center;gap:.4rem;min-width:64px;min-height:52px;padding:.35rem .5rem;border:1px solid transparent;border-radius:9px;background:transparent;color:#d7dfec;font:inherit;font-size:.83rem;white-space:nowrap;transition:color 180ms,background 180ms,border-color 180ms;}.concept-star:hover,.concept-star:focus-visible {border-color:#a5bddf45;background:#172337e8;color:#fff;}
.data-star {position:relative;width:6px;height:6px;flex:none;border-radius:50%;background:var(--constellation-color);box-shadow:0 0 9px color-mix(in srgb,var(--constellation-color) 70%,transparent);animation:breathe 4.8s ease-in-out infinite;animation-delay:var(--pulse-delay);}.data-star::after {content:"";position:absolute;inset:-6px;border:1px solid var(--constellation-color);border-radius:50%;opacity:0;transition:opacity 220ms;}.concept-star.selected .data-star::after,.concept-star:hover .data-star::after {opacity:.6;}
.concept-star.selected {color:#fff;}.concept-star.selected>span:nth-child(2) {text-shadow:0 0 16px #b2c4ff55;}.concept-star:disabled {color:#8b96a9;opacity:.6;cursor:default;}.concept-star:disabled .data-star {background:#65748c;box-shadow:none;animation:none;}
.concept-star :deep([data-learning-state='not_started']) {visibility:hidden;}.concept-star:hover :deep([data-learning-state='not_started']),.concept-star:focus-visible :deep([data-learning-state='not_started']) {visibility:visible;}
.shared-star {position:absolute;left:50%;top:50%;z-index:3;transform:translate(-50%,-50%);display:grid;justify-items:center;gap:.3rem;min-width:185px;padding:.8rem 1.1rem;border:1px solid #6c809b80;border-radius:12px;background:#142032f5;color:#e6edf8;box-shadow:0 8px 24px #00000020;animation:concept-arrive 350ms ease-out;}.shared-kicker {font-size:.6rem;letter-spacing:.13em;color:#9aadc7;}.shared-star strong {font-size:.85rem;font-weight:500;}.shared-star small {font-size:.65rem;color:#a4b7d0;}
.atlas-caption {display:flex;justify-content:center;flex-wrap:wrap;gap:.5rem 1.1rem;margin:0;padding:1rem 1.3rem;border-top:1px solid #ffffff0c;color:#9aa8bd;font-size:.7rem;line-height:1.7;}.atlas-caption>span {color:#d0dbeb;}
.motion-paused *,.motion-paused *::before,.motion-paused *::after {animation-play-state:paused!important;}
.motion-paused .shared-star {animation:none;}
@keyframes travel {to {stroke-dashoffset:-372;}}@keyframes local-travel {to {stroke-dashoffset:-196;}}@keyframes breathe {0%,100% {opacity:.58;}50% {opacity:1;}}
@keyframes stardust-drift {from {transform:scale(1.03);}to {transform:translate(8px,-6px) scale(1.08);}}@keyframes icon-float {0%,100% {transform:translateY(-2px);}50% {transform:translateY(2px);}}@keyframes concept-arrive {from {opacity:.45;filter:blur(2px);}to {opacity:1;filter:blur(0);}}
@media(max-width:65rem) {.knowledge-group small {display:none;}.atlas-legend p {display:none;}.concept-star {font-size:.76rem;min-width:54px;}}
@media(max-width:52rem) {
 .home-atlas {border-radius:15px;}.atlas-legend {gap:1rem;padding:1rem;}.atlas-eyebrow {font-size:.5rem;}.atlas-legend strong {font-size:.9rem;}.motion-toggle {padding:.5rem .6rem;font-size:.65rem;}
 .atlas-scene {grid-template-columns:minmax(0,1fr);height:auto;padding-top:92px;}.language-constellation {height:310px;border-top:1px solid #ffffff0c;}.shared-star {left:1rem;right:1rem;top:16px;min-width:0;transform:none;padding:.65rem;}.shared-kicker {display:none;}.semantic-bridges {display:none;}
 .language-heading {left:0;width:27%;}.language-heading strong {font-size:1.25rem;}.language-heading img {width:34px;height:34px;}.language-heading small:last-child {font-size:.56rem;}.knowledge-group {left:34%;}.knowledge-group strong {font-size:.65rem;}.concept-star {min-width:44px;padding-inline:.15rem;font-size:.7rem;}.atlas-caption {justify-content:flex-start;padding:1rem;line-height:1.8;}.drifting-stars {opacity:.22;}
}
@media(prefers-reduced-motion:reduce) {*,*::before,*::after {animation:none!important;transition:none!important;}.drifting-stars img {transform:none;}}
</style>
