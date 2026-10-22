<script setup lang="ts">
import MapWorld from "./MapWorld.vue";
import { languageWorlds, orbitRings } from "./map-layout";
import type { MapSnapshot } from "./map.store";

defineProps<{ snapshot: Readonly<MapSnapshot> }>();
</script>

<template>
  <section class="orbital-map" aria-label="桌面知识星图">
    <span v-for="ring in orbitRings" :key="ring" class="orbit-ring" :style="{ width: `${ring}%`, aspectRatio: '1' }" aria-hidden="true"></span>
    <MapWorld v-for="world in languageWorlds" :key="world.id" :world="world" :state="snapshot.languages[world.id]" />
    <RouterLink v-if="snapshot.continueLessonId" class="continue-node" :to="`/lesson/${snapshot.continueLessonId}`" data-continue-learning>
      <span class="continue-node__eyebrow">继续学习</span>
      <strong>{{ snapshot.continueLessonTitle }}</strong>
      <span>打开课时</span>
    </RouterLink>
    <p v-else class="continue-node">{{ snapshot.continueLessonTitle }}</p>
  </section>
</template>

<style scoped>
.orbital-map {
  position: relative;
  isolation: isolate;
  height: clamp(29rem, calc(100dvh - 21rem), 39rem);
  overflow: hidden;
  border: 0.0625rem solid color-mix(in srgb, var(--hard-color-primary) 34%, var(--hard-color-line));
  border-radius: var(--hard-radius-lg);
  background:
    radial-gradient(circle at 50% 50%, rgb(138 92 255 / 34%), transparent 17%),
    radial-gradient(circle at 50% 50%, transparent 38%, rgb(3 8 21 / 80%) 100%),
    radial-gradient(circle at 18% 18%, rgb(77 229 231 / 20%) 0 0.08rem, transparent 0.13rem),
    radial-gradient(circle at 78% 14%, rgb(244 246 255 / 70%) 0 0.07rem, transparent 0.11rem),
    radial-gradient(circle at 88% 70%, rgb(167 139 255 / 44%) 0 0.09rem, transparent 0.14rem),
    radial-gradient(circle at 29% 84%, rgb(244 246 255 / 50%) 0 0.06rem, transparent 0.1rem),
    var(--hard-color-space);
  box-shadow: inset 0 0 5rem rgb(0 0 0 / 42%), var(--hard-shadow-raised);
}

.orbit-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  border: 0.0625rem solid var(--hard-color-line);
  border-radius: 50%;
  box-shadow: 0 0 2rem rgb(138 92 255 / 11%), inset 0 0 1.5rem rgb(77 229 231 / 5%);
  transform: translate(-50%, -50%);
}

.orbit-ring:nth-of-type(2) { border-color: color-mix(in srgb, var(--hard-color-primary) 45%, var(--hard-color-line)); }
.orbit-ring:nth-of-type(3) { border-color: color-mix(in srgb, var(--hard-color-cyan) 30%, var(--hard-color-line)); }

.continue-node {
  position: absolute;
  left: 50%;
  top: 50%;
  display: grid;
  place-items: center;
  gap: var(--hard-space-1);
  z-index: 1;
  width: clamp(13rem, 20vw, 18rem);
  min-height: clamp(13rem, 20vw, 18rem);
  padding: var(--hard-space-5);
  border: 0.1875rem solid var(--hard-color-primary-strong);
  border-radius: 50%;
  color: var(--hard-color-text);
  background: radial-gradient(circle at 35% 28%, rgb(193 174 255 / 64%), rgb(88 57 191 / 82%) 46%, rgb(16 27 55 / 94%) 100%);
  box-shadow: 0 0 2.5rem rgb(138 92 255 / 58%), inset -1rem -1rem 2.5rem rgb(3 8 21 / 46%);
  text-align: center;
  text-decoration: none;
  transform: translate(-50%, -50%);
  transition: transform var(--hard-motion-fast) ease;
}

.continue-node:hover,
.continue-node:focus-visible { transform: translate(-50%, -50%) scale(1.04); }
.continue-node__eyebrow { color: var(--hard-color-text); font-size: var(--hard-text-md); font-weight: 800; letter-spacing: 0.08em; }
.continue-node strong { font-size: var(--hard-text-xl); line-height: 1.1; }
.continue-node span:last-child { color: var(--hard-color-text); font-size: var(--hard-text-sm); font-weight: 700; }
</style>
