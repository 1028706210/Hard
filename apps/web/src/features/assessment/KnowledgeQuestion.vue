<script setup lang="ts">
import { ref } from "vue";

import type { Exercise } from "./assessment.store";

const props = defineProps<{ exercise: Pick<Exercise, "id" | "type" | "prompt" | "choices"> }>();
const emit = defineEmits<{ submit: [answer: string, hintLevel: string] }>();
const answer = ref("");
const hintLevel = ref("none");
</script>

<template>
  <section class="knowledge-question">
    <p>{{ props.exercise.prompt }}</p>
    <div class="knowledge-question__choices" role="radiogroup" aria-label="答案选项">
      <button v-for="choice in props.exercise.choices" :key="choice.id" type="button" :aria-pressed="answer === choice.id" @click="answer = choice.id">{{ choice.text }}</button>
    </div>
    <div class="knowledge-question__hints">
      <button type="button" @click="hintLevel = 'light'">轻提示</button>
      <button type="button" @click="hintLevel = 'strong'">强提示</button>
      <p v-if="hintLevel === 'light'">轻提示后本题最高 85% 分</p>
      <p v-else-if="hintLevel === 'strong'">强提示后本题最高 60% 分</p>
    </div>
    <button class="knowledge-question__submit" type="button" :disabled="!answer" @click="emit('submit', answer, hintLevel)">提交答案</button>
  </section>
</template>

<style scoped>
.knowledge-question { display: grid; gap: var(--hard-space-3); }
.knowledge-question__choices, .knowledge-question__hints { display: flex; flex-wrap: wrap; gap: var(--hard-space-2); }
button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-surface-raised); font: inherit; cursor: pointer; }
button[aria-pressed="true"], .knowledge-question__submit { border-color: var(--hard-color-primary); background: var(--hard-color-primary); }
p { margin: 0; color: var(--hard-color-muted); }
</style>
