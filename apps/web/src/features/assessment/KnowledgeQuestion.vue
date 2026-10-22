<script setup lang="ts">
import { computed, nextTick, ref } from "vue";

import type { Exercise } from "./assessment.store";

const props = defineProps<{ exercise: Pick<Exercise, "id" | "type" | "prompt" | "choices"> }>();
const emit = defineEmits<{ submit: [answer: string, hintLevel: string] }>();
const answers = ref<Record<string, string>>({});
const hints = ref<Record<string, string>>({});
const answer = computed({ get: () => answers.value[props.exercise.id] ?? "", set: (value: string) => { answers.value[props.exercise.id] = value; } });
const hintLevel = computed({ get: () => hints.value[props.exercise.id] ?? "none", set: (value: string) => { hints.value[props.exercise.id] = value; } });
const optionInputs = new Map<string, HTMLInputElement>();

function setOptionInput(choiceId: string, element: unknown) {
  if (element instanceof HTMLInputElement) optionInputs.set(choiceId, element);
  else optionInputs.delete(choiceId);
}
function selectByKeyboard(index: number, event: KeyboardEvent) {
  const choices = props.exercise.choices;
  if (!choices.length) return;
  const key = event.key;
  if (key === " " || key === "Spacebar" || key === "Enter") { answer.value = choices[index]!.id; return; }
  const direction = key === "ArrowRight" || key === "ArrowDown" ? 1 : key === "ArrowLeft" || key === "ArrowUp" ? -1 : 0;
  if (!direction) return;
  event.preventDefault();
  const nextIndex = (index + direction + choices.length) % choices.length;
  const next = choices[nextIndex]!;
  answer.value = next.id;
  void nextTick(() => optionInputs.get(next.id)?.focus());
}
</script>

<template>
  <section class="knowledge-question">
    <p>{{ props.exercise.prompt }}</p>
    <fieldset class="knowledge-question__choices"><legend>答案选项</legend>
      <label v-for="(choice, index) in props.exercise.choices" :key="`${props.exercise.id}:${choice.id}`" :class="{ 'is-selected': answer === choice.id }">
        <input :ref="(element) => setOptionInput(choice.id, element)" type="radio" :name="`knowledge-${props.exercise.id}`" :value="choice.id" :checked="answer === choice.id" @change="answer = choice.id" @keydown="selectByKeyboard(index, $event)" />
        <span class="knowledge-question__choice-letter" aria-hidden="true">{{ String.fromCharCode(65 + index) }}</span><span>{{ choice.text }}</span>
      </label>
    </fieldset>
    <div class="knowledge-question__hints">
      <span class="knowledge-question__hint-label">需要一点帮助？</span>
      <button type="button" :aria-pressed="hintLevel === 'light'" @click="hintLevel = 'light'">轻提示</button>
      <button type="button" :aria-pressed="hintLevel === 'strong'" @click="hintLevel = 'strong'">强提示</button>
      <p v-if="hintLevel === 'light'">轻提示后本题最高 85% 分</p>
      <p v-else-if="hintLevel === 'strong'">强提示后本题最高 60% 分</p>
    </div>
    <button class="knowledge-question__submit" type="button" :disabled="!answer" @click="emit('submit', answer, hintLevel)">提交答案</button>
  </section>
</template>

<style scoped>
.knowledge-question { display: grid; gap: 1.5rem; max-width: 48rem; }
.knowledge-question > p { color: var(--hard-color-text); font-size: clamp(1.05rem, 1.5vw, 1.2rem); font-weight: 500; line-height: 1.85; }
.knowledge-question__choices, .knowledge-question__hints { display: flex; flex-wrap: wrap; gap: var(--hard-space-2); min-width: 0; margin: 0; padding: 0; border: 0; }
.knowledge-question__choices legend { padding: 0; color: var(--hard-color-muted); }
.knowledge-question__choices { display: grid; gap: .75rem; }
.knowledge-question__choices legend { margin-bottom: .75rem; font-size: .875rem; }
.knowledge-question__choices label { display: flex; align-items: center; gap: .85rem; min-height: 60px; padding: 1rem; border: 1px solid var(--hard-color-line); border-radius: var(--hard-radius-sm); background: transparent; cursor: pointer; font-size: .95rem; line-height: 1.7; transition: border-color .16s ease, background .16s ease; }
.knowledge-question__choice-letter { flex-shrink: 0; color: var(--hard-color-muted); font: .75rem ui-monospace, monospace; }
.knowledge-question__choices label:hover { background: var(--hard-color-surface-raised); }
.knowledge-question__choices label.is-selected { border-color: var(--hard-color-primary-strong); background: color-mix(in srgb, var(--hard-color-primary) 14%, transparent); }
.knowledge-question__choices input { flex-shrink: 0; }
.knowledge-question__hints { align-items: center; padding-top: .5rem; }
.knowledge-question__hint-label { margin-right: .5rem; color: var(--hard-color-muted); font-size: .8rem; }
.knowledge-question__hints button { min-height: 40px; padding-inline: .85rem; font-size: .8rem; background: transparent; }
.knowledge-question__hints p { flex-basis: 100%; font-size: .875rem; }
.knowledge-question__submit { justify-self: start; min-width: 10rem; }
.knowledge-question__choices input { inline-size: 1.125rem; block-size: 1.125rem; accent-color: var(--hard-color-primary); }
button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-surface-raised); font: inherit; cursor: pointer; }
button[aria-pressed="true"], .knowledge-question__submit { border-color: var(--hard-color-primary); background: var(--hard-color-primary); }
button:disabled { opacity: .45; cursor: not-allowed; }
p { margin: 0; color: var(--hard-color-muted); }
@media (max-width: 40rem) { .knowledge-question__choices label { padding: .85rem; gap: .65rem; } .knowledge-question__hint-label { flex-basis: 100%; margin-bottom: .25rem; } .knowledge-question__submit { width: 100%; } }
@media (prefers-reduced-motion: reduce) { .knowledge-question__choices label { transition: none; } }
</style>
