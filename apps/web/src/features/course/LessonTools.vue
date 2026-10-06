<script setup lang="ts">
defineProps<{ modelValue: string; favorite: boolean; syncStatus: string }>();
defineEmits<{ "update:modelValue": [value: string]; save: []; retry: []; favorite: [] }>();
</script>

<template>
  <aside class="lesson-tools" aria-label="课时工具">
    <label for="lesson-note">课时笔记</label>
    <textarea id="lesson-note" :value="modelValue" rows="8" @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"></textarea>
    <p aria-live="polite">{{ syncStatus === "failed" ? "同步失败，草稿已保留" : syncStatus === "synced" ? "已同步" : syncStatus === "syncing" ? "同步中" : "未同步" }}</p>
    <div class="lesson-tools__actions">
      <button type="button" @click="$emit('save')">保存笔记</button>
      <button v-if="syncStatus === 'failed'" type="button" @click="$emit('retry')">重试保存</button>
      <button type="button" @click="$emit('favorite')">{{ favorite ? "取消收藏" : "收藏课时" }}</button>
    </div>
  </aside>
</template>

<style scoped>
.lesson-tools { align-self: start; display: grid; gap: var(--hard-space-2); padding: var(--hard-space-4); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-md); background: var(--hard-color-surface); }
textarea { width: 100%; min-height: 10rem; resize: vertical; padding: var(--hard-space-3); border: 0.0625rem solid var(--hard-color-line); border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-space); font: inherit; }
p { min-height: 1.25rem; margin: 0; color: var(--hard-color-muted); font-size: var(--hard-text-sm); }
.lesson-tools__actions { display: flex; flex-wrap: wrap; gap: var(--hard-space-2); }
button { min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; cursor: pointer; }
button:last-child { background: var(--hard-color-surface-raised); }
</style>
