<script setup lang="ts">
import { ref } from "vue";

import { requestJson } from "../../api/client";

interface ExportedArchive { archive_name: string; content_version: string; }
interface ImportedArchive { content_version: string; }
const archive = ref<ExportedArchive | null>(null);
const selectedFile = ref<File | null>(null);
const status = ref("");
const error = ref("");

function key(prefix: string) { return `${prefix}-${globalThis.crypto?.randomUUID?.() ?? Date.now()}`; }
function selectArchive(event: Event) {
  const input = event.target as HTMLInputElement;
  selectedFile.value = input.files?.[0] ?? null;
}
async function exportData() {
  status.value = "";
  error.value = "";
  try {
    archive.value = await requestJson<ExportedArchive>("/api/backup/export", {
      method: "POST",
      headers: { "Idempotency-Key": key("export") },
    });
    status.value = "导出包已生成，请复制到另一块磁盘。";
  } catch { error.value = "无法创建导出包，请确认本机数据目录可写。"; }
}
async function importData() {
  if (!selectedFile.value) return;
  status.value = "";
  error.value = "";
  try {
    const result = await requestJson<ImportedArchive>("/api/backup/import", {
      method: "POST",
      headers: { "X-Archive-Name": selectedFile.value.name, "Idempotency-Key": key("import") },
      body: selectedFile.value,
    });
    status.value = `导入完成，内容版本：${result.content_version}`;
  } catch { error.value = "导入失败，原有学习数据已保持可用。"; }
}
</script>

<template>
  <section class="data-management" aria-labelledby="data-management-title">
    <div><h2 id="data-management-title">数据管理</h2><p>本机导出包包含数据库、设置清单、内容版本和 SHA-256 校验清单。</p></div>
    <p class="warning"><strong>同一 D 盘备份不能防止硬盘损坏</strong>；请把手动导出包复制到另一块磁盘。</p>
    <div class="actions"><button type="button" @click="exportData">创建导出包</button><span v-if="archive" data-export-name>已保存至 exports/{{ archive.archive_name }}</span></div>
    <label>选择导入归档<input type="file" accept="application/zip,.zip" @change="selectArchive"></label>
    <button data-import-archive type="button" :disabled="!selectedFile" @click="importData">安全导入</button>
    <p v-if="status" class="notice notice--success" role="status">{{ status }}</p><p v-if="error" class="notice notice--error" role="alert">{{ error }}</p>
  </section>
</template>

<style scoped>
.data-management { display: grid; gap: var(--hard-space-3); } h2 { margin: 0; font-size: var(--hard-text-lg); } p { margin: 0; color: var(--hard-color-muted); line-height: 1.65; } .warning strong { color: var(--hard-color-amber); } .actions { display: flex; flex-wrap: wrap; align-items: center; gap: var(--hard-space-2); } button { display: inline-flex; align-items: center; justify-content: center; min-height: var(--hard-touch-target); padding: 0 var(--hard-space-3); border: 0; border-radius: var(--hard-radius-sm); color: var(--hard-color-text); background: var(--hard-color-primary); font: inherit; cursor: pointer; } .actions span { color: var(--hard-color-cyan); overflow-wrap: anywhere; } button:disabled { cursor: not-allowed; opacity: .55; } label { display: grid; gap: var(--hard-space-1); color: var(--hard-color-muted); font-size: var(--hard-text-sm); } input { min-height: var(--hard-touch-target); color: var(--hard-color-text); } .notice { padding: var(--hard-space-3); border-radius: var(--hard-radius-sm); } .notice--success { color: var(--hard-color-cyan); background: color-mix(in srgb, var(--hard-color-cyan) 12%, transparent); } .notice--error { color: var(--hard-color-danger); background: color-mix(in srgb, var(--hard-color-danger) 12%, transparent); }
</style>
