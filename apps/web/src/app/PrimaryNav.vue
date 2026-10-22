<script setup lang="ts">
import { computed } from "vue";
import { learningDestinations } from "./router";
const props = defineProps<{ lessonId?: string }>();
const destinations = computed(() => learningDestinations(props.lessonId));
</script>

<template>
  <nav class="primary-nav" aria-label="主导航">
    <RouterLink v-for="destination in destinations" :key="destination.path" :to="destination.path">
      {{ destination.label }}
    </RouterLink>
  </nav>
</template>
