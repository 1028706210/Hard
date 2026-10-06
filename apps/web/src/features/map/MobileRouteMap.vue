<script setup lang="ts">
import { languageWorlds, statusLabels } from "./map-layout";
import type { MapSnapshot } from "./map.store";
defineProps<{ snapshot: Readonly<MapSnapshot> }>();
</script>

<template>
  <section class="mobile-route" data-mobile-route aria-label="手机学习路线">
    <ol>
      <li v-for="world in languageWorlds" :key="world.id" :data-route-node="world.id">
        <RouterLink :to="`/course/${world.id}`">
          <span class="mobile-route__marker" :class="`mobile-route__marker--${snapshot.languages[world.id].status}`" aria-hidden="true"></span>
          <span><strong>{{ world.title }}</strong><small>{{ snapshot.languages[world.id].label }}</small></span>
          <span class="mobile-route__status">{{ snapshot.languages[world.id].label }}</span>
        </RouterLink>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.mobile-route { display: none; }

@media (max-width: 52rem) {
  .mobile-route { display: block; }
  ol { display: grid; gap: var(--hard-space-3); margin: 0; padding: 0; list-style: none; }
  li { position: relative; }
  li:not(:last-child)::after { position: absolute; left: 1.375rem; top: 2.75rem; width: 0.125rem; height: var(--hard-space-3); background: var(--hard-color-line); content: ""; }
  a { display: grid; grid-template-columns: 2.75rem 1fr auto; align-items: center; gap: var(--hard-space-3); min-height: 4.75rem; padding: var(--hard-space-3); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); color: var(--hard-color-text); background: var(--hard-color-surface-raised); text-decoration: none; }
  strong, small { display: block; }
  small { margin-top: var(--hard-space-1); color: var(--hard-color-muted); }
  .mobile-route__marker { width: 1rem; height: 1rem; border-radius: 50%; background: var(--hard-color-primary); box-shadow: var(--hard-shadow-glow); }
  .mobile-route__marker--not_started { background: var(--hard-color-cyan); }
  .mobile-route__marker--mastered { background: var(--hard-color-amber); }
  .mobile-route__marker--locked { background: var(--hard-color-danger); }
  .mobile-route__marker--unavailable { background: var(--hard-color-muted); box-shadow: none; }
  .mobile-route__status { color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
}
</style>
