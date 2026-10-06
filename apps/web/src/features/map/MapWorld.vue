<script setup lang="ts">
import type { LanguageWorld } from "./map-layout";
import type { MapLanguageState } from "./map.store";

const props = defineProps<{ world: LanguageWorld; state: MapLanguageState }>();
</script>

<template>
  <RouterLink
    class="map-world"
    :class="`map-world--${props.state.status}`"
    :to="`/course/${props.world.id}`"
    :style="{ '--world-x': `${props.world.x}%`, '--world-y': `${props.world.y}%` }"
    :aria-label="`${props.world.title}，${props.state.label}`"
    :data-map-world="props.world.id"
  >
    <span class="map-world__orbit" aria-hidden="true"></span>
    <span class="map-world__title">{{ props.world.title }}</span>
    <span class="map-world__status">{{ props.state.label }}</span>
    <span class="map-world__detail">{{ props.state.available ? '课程路线' : '等待内容' }}</span>
  </RouterLink>
</template>

<style scoped>
.map-world {
  position: absolute;
  left: var(--world-x);
  top: var(--world-y);
  display: grid;
  place-items: center;
  width: clamp(6.5rem, 11vw, 9.25rem);
  min-height: clamp(6.5rem, 11vw, 9.25rem);
  padding: var(--hard-space-2);
  border: 0.125rem solid var(--world-color, var(--hard-color-primary));
  border-radius: 50%;
  color: var(--hard-color-text);
  background: color-mix(in srgb, var(--hard-color-surface-raised) 88%, var(--world-color, var(--hard-color-primary)));
  box-shadow: 0 0 2rem color-mix(in srgb, var(--world-color, var(--hard-color-primary)) 42%, transparent);
  text-align: center;
  text-decoration: none;
  transform: translate(-50%, -50%);
  transition: transform var(--hard-motion-fast) ease, box-shadow var(--hard-motion-fast) ease;
}

.map-world:hover,
.map-world:focus-visible {
  transform: translate(-50%, -50%) scale(1.05);
}

.map-world--in_progress { --world-color: var(--hard-color-primary); }
.map-world--not_started { --world-color: var(--hard-color-cyan); }
.map-world--mastered { --world-color: var(--hard-color-amber); }
.map-world--locked { --world-color: var(--hard-color-danger); }
.map-world--unavailable { --world-color: var(--hard-color-muted); }

.map-world__orbit {
  position: absolute;
  inset: -0.5rem;
  border: 0.0625rem solid var(--world-color, var(--hard-color-primary));
  border-radius: inherit;
  opacity: 0.45;
}

.map-world__title { font-size: var(--hard-text-lg); font-weight: 800; }
.map-world__status { color: var(--world-color, var(--hard-color-primary)); font-size: var(--hard-text-sm); font-weight: 700; }
.map-world__detail { color: var(--hard-color-muted); font-size: var(--hard-text-xs); }
</style>
