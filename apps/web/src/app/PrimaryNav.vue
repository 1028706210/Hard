<script setup lang="ts">
import { destinations } from "./router";
</script>

<template>
  <nav class="primary-nav" aria-label="主导航">
    <RouterLink v-for="destination in destinations" :key="destination.path" :to="destination.path">
      {{ destination.label }}
    </RouterLink>
  </nav>
</template>
