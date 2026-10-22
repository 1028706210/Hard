<script setup lang="ts">
import { useMapStore } from "./map.store";
defineProps<{ lessonId?: string | null }>();
const snapshot = useMapStore();
</script>

<template>
  <small v-if="lessonId && snapshot.lessons[lessonId]" class="lesson-progress" :data-learning-state="snapshot.lessons[lessonId].status">{{ snapshot.lessons[lessonId].label }}</small>
</template>

<style scoped>
.lesson-progress { font-size:.65rem; line-height:1.3; color:#9caec5; }
[data-learning-state='in_progress'] { color:#b5c9ff; }
[data-learning-state='completed'],[data-learning-state='mastered'] { color:#93e3be; }
[data-learning-state='due_review'] { color:#f0cb85; }
</style>
