<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { ApiClientError, requestJson } from "../../api/client";

interface LanStatus { enabled: boolean; bind_host: string; port: number; url: string | null; interfaces: string[]; warning: string; firewall_preview: string; firewall_revoke_preview: string; }
const status = ref<LanStatus | null>(null);
const host = ref("");
const confirmed = ref(false);
const error = ref("");
function key() { return `lan-${globalThis.crypto?.randomUUID?.() ?? Date.now()}`; }

/* Version 3-L byte-mode QR encoder for short local URLs; no network or third-party code is used. */
function gfMultiply(left: number, right: number) { let result = 0; let a = left; let b = right; while (b) { if (b & 1) result ^= a; a = (a << 1) ^ (a & 0x80 ? 0x11d : 0); b >>>= 1; } return result; }
function gfPowerOfTwo(exponent: number) { let value = 1; for (let index = 0; index < exponent; index += 1) value = gfMultiply(value, 2); return value; }
function qrMatrix(text: string): boolean[][] {
  const size = 29; const cells: Array<Array<boolean | null>> = Array.from({ length: size }, () => Array<boolean | null>(size).fill(null));
  const set = (x: number, y: number, value: boolean) => { if (x >= 0 && x < size && y >= 0 && y < size) cells[y]![x] = value; };
  const finder = (left: number, top: number) => { for (let y = -1; y <= 7; y += 1) for (let x = -1; x <= 7; x += 1) set(left + x, top + y, x >= 0 && x <= 6 && y >= 0 && y <= 6 && (x === 0 || x === 6 || y === 0 || y === 6 || (x >= 2 && x <= 4 && y >= 2 && y <= 4))); };
  finder(0, 0); finder(size - 7, 0); finder(0, size - 7);
  for (let index = 8; index < size - 8; index += 1) { set(index, 6, index % 2 === 0); set(6, index, index % 2 === 0); }
  for (let y = 20; y <= 24; y += 1) for (let x = 20; x <= 24; x += 1) set(x, y, x === 20 || x === 24 || y === 20 || y === 24 || (x === 22 && y === 22));
  const format = (x: number, y: number) => set(x, y, false);
  for (let i = 0; i <= 5; i += 1) { format(8, i); format(i, 8); }
  format(8, 7); format(8, 8); format(7, 8); for (let i = 9; i < 15; i += 1) { format(8, 14 - i); format(size - 15 + i, 8); } for (let i = 0; i < 8; i += 1) format(size - 1 - i, 8); set(8, size - 8, true);
  const bytes = [...new TextEncoder().encode(text)].slice(0, 53); const bits: number[] = [0, 1, 0, 0]; for (let i = 7; i >= 0; i -= 1) bits.push((bytes.length >>> i) & 1); for (const byte of bytes) for (let i = 7; i >= 0; i -= 1) bits.push((byte >>> i) & 1); for (let i = 0; i < Math.min(4, 440 - bits.length); i += 1) bits.push(0); while (bits.length % 8) bits.push(0);
  const data: number[] = []; for (let i = 0; i < bits.length; i += 8) data.push(bits.slice(i, i + 8).reduce((value, bit) => (value << 1) | bit, 0)); for (let pad = 0; data.length < 55; pad += 1) data.push(pad % 2 ? 0x11 : 0xec);
  let generator = [1]; for (let degree = 0; degree < 15; degree += 1) { const next = Array(generator.length + 1).fill(0); for (let i = 0; i < generator.length; i += 1) { next[i] ^= generator[i]!; next[i + 1] ^= gfMultiply(generator[i]!, gfPowerOfTwo(degree)); } generator = next; }
  const remainder = [...data, ...Array(15).fill(0)]; for (let i = 0; i < data.length; i += 1) { const factor = remainder[i]!; if (factor) for (let j = 0; j < generator.length; j += 1) remainder[i + j] ^= gfMultiply(generator[j]!, factor); } const codewords = [...data, ...remainder.slice(-15)]; const stream = codewords.flatMap((word) => Array.from({ length: 8 }, (_, index) => (word >>> (7 - index)) & 1));
  let index = 0; let upward = true; for (let right = size - 1; right > 0; right -= 2) { if (right === 6) right -= 1; for (let offset = 0; offset < size; offset += 1) { const y = upward ? size - 1 - offset : offset; for (let x = right; x >= right - 1; x -= 1) if (cells[y]![x] === null) { const bit = stream[index++] ?? 0; set(x, y, Boolean(bit ^ ((x + y) % 2 === 0 ? 1 : 0))); } } upward = !upward; }
  let dataBits = 0b01000; let remainderBits = dataBits; for (let i = 0; i < 10; i += 1) remainderBits = (remainderBits << 1) ^ ((remainderBits >>> 9) * 0x537); const formatBits = ((dataBits << 10) | remainderBits) ^ 0x5412; const bit = (index: number) => ((formatBits >>> index) & 1) === 1;
  for (let i = 0; i <= 5; i += 1) set(8, i, bit(i)); set(8, 7, bit(6)); set(8, 8, bit(7)); set(7, 8, bit(8)); for (let i = 9; i < 15; i += 1) set(8, 14 - i, bit(i)); for (let i = 0; i < 8; i += 1) set(size - 1 - i, 8, bit(i)); for (let i = 8; i < 15; i += 1) set(size - 15 + i, 8, bit(i));
  return cells.map((row) => row.map(Boolean));
}

const modules = computed(() => {
  const matrix = status.value?.url ? qrMatrix(status.value.url) : [];
  return matrix.flatMap((row, y) => row.flatMap((dark, x) => dark ? [{ x, y }] : []));
});
async function load() { try { status.value = await requestJson<LanStatus>("/api/lan/status"); host.value = status.value.interfaces[0] ?? ""; } catch { error.value = "无法读取局域网状态。"; } }
async function enable() { if (!confirmed.value || !host.value) return; error.value = ""; try { status.value = await requestJson<LanStatus>("/api/lan/enable", { method: "POST", headers: { "content-type": "application/json", "Idempotency-Key": key() }, body: JSON.stringify({ host: host.value, confirmed: true }) }); } catch (raised) { const body = raised instanceof ApiClientError ? raised.body as { error?: { code?: string; message?: string } } : undefined; error.value = body?.error?.code === "lan_frontend_build_required" ? (body.error.message ?? "请先构建 Hard 前端：pnpm --dir apps/web build。") : "局域网访问未启用；请重新确认所选私有接口。"; } }
async function disable() { error.value = ""; try { status.value = await requestJson<LanStatus>("/api/lan/enable", { method: "DELETE" }); } catch { error.value = "局域网访问停止失败；请重试。"; } }
onMounted(load);
</script>

<template>
  <section class="lan-access" aria-labelledby="lan-title"><h2 id="lan-title">手机访问</h2><p>{{ status?.warning ?? "同一网络设备可访问数据并运行代码。" }}</p><p>默认只监听本机 loopback。这里仅生成私有网络启动配置与防火墙预览，绝不会执行防火墙命令。</p><label>私有 IPv4 接口<select v-model="host"><option v-for="item in status?.interfaces ?? []" :key="item" :value="item">{{ item }}</option></select></label><label class="acknowledgement"><input v-model="confirmed" type="checkbox" aria-label="我已理解局域网访问风险">我已理解局域网访问风险</label><button v-if="!status?.enabled" type="button" :disabled="!confirmed || !host" @click="enable">启用局域网访问</button><button v-else type="button" @click="disable">停止局域网访问</button><p v-if="error" role="alert" class="error">{{ error }}</p><template v-if="status?.enabled && status.url"><p class="url">{{ status.url }}</p><svg data-qr-code viewBox="0 0 29 29" role="img" aria-label="局域网地址二维码"><rect width="29" height="29" fill="white"/><rect v-for="module in modules" :key="`${module.y}-${module.x}`" :x="module.x" :y="module.y" width="1" height="1" fill="black"/></svg><details><summary>防火墙命令预览（未执行）</summary><code>{{ status.firewall_preview }}</code><code>{{ status.firewall_revoke_preview }}</code></details></template></section>
</template>

<style scoped>
.lan-access { display: grid; gap: var(--hard-space-3); } h2, p { margin: 0; } p { color: var(--hard-color-muted); line-height: 1.65; } label { display: grid; gap: var(--hard-space-1); color: var(--hard-color-muted); } select, button { min-height: var(--hard-touch-target); border-radius: var(--hard-radius-sm); font: inherit; } select { padding: 0 var(--hard-space-2); border: .0625rem solid var(--hard-color-line); color: var(--hard-color-text); background: var(--hard-color-space); } .acknowledgement { display: flex; align-items: center; gap: var(--hard-space-2); } button { padding: 0 var(--hard-space-3); border: 0; color: var(--hard-color-text); background: var(--hard-color-primary); cursor: pointer; } button:disabled { opacity: .55; cursor: not-allowed; } .url { color: var(--hard-color-cyan); font-weight: 700; overflow-wrap: anywhere; } svg { width: min(13rem, 100%); padding: var(--hard-space-2); border-radius: var(--hard-radius-sm); background: white; image-rendering: pixelated; } details { display: grid; gap: var(--hard-space-2); color: var(--hard-color-muted); } code { overflow-wrap: anywhere; color: var(--hard-color-amber); } .error { color: var(--hard-color-danger); }
</style>
