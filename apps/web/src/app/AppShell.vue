<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import MobileNav from "./MobileNav.vue";
import PrimaryNav from "./PrimaryNav.vue";
import { createOfflineDraftQueue } from "./offline-drafts";

const mobileNavigationOpen = ref(false);
const navigationTrigger = ref<HTMLButtonElement>();
const activeLessonId = ref<string>();
const route = useRoute();
watch(() => route.params.lessonId, value => { if (typeof value === "string") activeLessonId.value = value; }, { immediate: true });
watch(() => route.fullPath, () => { mobileNavigationOpen.value = false; });
function closeNavigation(event: KeyboardEvent) {
  if (event.key !== "Escape" || !mobileNavigationOpen.value) return;
  mobileNavigationOpen.value = false;
  void nextTick(() => navigationTrigger.value?.focus());
}
onMounted(() => window.addEventListener("keydown", closeNavigation));
onBeforeUnmount(() => window.removeEventListener("keydown", closeNavigation));
const queue = createOfflineDraftQueue();
const drafts = ref(queue.items());
const pendingDrafts = computed(() => drafts.value.filter((draft) => draft.state !== "failed_runner").length);
const failedDrafts = computed(() => drafts.value.filter((draft) => draft.state === "failed_runner"));
async function syncOfflineDrafts() { if (!navigator.onLine) return; await queue.flush(); drafts.value = queue.items(); }
function retryKey(key: string) {
  const nonce = globalThis.crypto?.randomUUID?.() ?? `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 14)}`;
  return `${key.slice(0, Math.max(1, 127 - nonce.length))}:${nonce}`.slice(0, 128);
}
function retryDraft(key: string) { queue.retry(key, retryKey(key)); void syncOfflineDrafts(); }
function removeDraft(key: string) { queue.remove(key); drafts.value = queue.items(); }
onMounted(() => { window.addEventListener("online", syncOfflineDrafts); void syncOfflineDrafts(); });
onBeforeUnmount(() => window.removeEventListener("online", syncOfflineDrafts));
</script>

<template>
  <div class="app-shell">
    <a class="skip-link" href="#main-content">跳到主要内容</a>
    <header class="app-header">
      <RouterLink class="hard-brand" to="/" aria-label="Hard 知识星图主页">HARD<span class="brand-caption" aria-hidden="true">LEARN · BUILD · GROW</span></RouterLink>
      <PrimaryNav :lesson-id="activeLessonId" />
      <button
        class="mobile-nav-trigger"
        ref="navigationTrigger"
        type="button"
        aria-label="打开导航"
        aria-controls="mobile-navigation"
        :aria-expanded="mobileNavigationOpen"
        @click="mobileNavigationOpen = !mobileNavigationOpen"
      >
        菜单
      </button>
      <MobileNav v-if="mobileNavigationOpen" :lesson-id="activeLessonId" @close="mobileNavigationOpen = false" />
    </header>
    <main id="main-content" class="app-main" tabindex="-1">
      <p v-if="pendingDrafts" class="offline-notice" role="status">有 {{ pendingDrafts }} 项离线草稿待同步。</p>
      <section v-if="failedDrafts.length" class="offline-notice" aria-label="离线运行失败" role="alert" aria-live="assertive">
        <p v-for="draft in failedDrafts" :key="draft.idempotencyKey">运行未完成（{{ draft.failureReason }}）。<button type="button" @click="retryDraft(draft.idempotencyKey)">重试</button><button type="button" @click="removeDraft(draft.idempotencyKey)">删除</button></p>
      </section>
      <RouterView />
    </main>
  </div>
</template>
