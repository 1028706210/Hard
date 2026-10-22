<script setup lang="ts">
import { computed } from "vue";
import { learningDestinations } from "./router";
const props = defineProps<{ lessonId?: string }>();
const destinations = computed(() => learningDestinations(props.lessonId));

defineEmits<{ close: [] }>();
</script>

<template>
  <nav id="mobile-navigation" class="mobile-nav" aria-label="移动导航">
    <RouterLink v-for="destination in destinations" :key="destination.path" :to="destination.path" @click="$emit('close')">
      {{ destination.label }}
    </RouterLink>
  </nav>
</template>
