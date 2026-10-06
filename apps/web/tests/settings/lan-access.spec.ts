import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import LanAccess from "../../src/features/settings/LanAccess.vue";


const inactive = { enabled: false, bind_host: "127.0.0.1", port: 8000, url: null, interfaces: ["192.168.10.8"], warning: "同一网络设备可访问数据并运行代码。", firewall_preview: "preview", firewall_revoke_preview: "revoke" };
const active = { ...inactive, enabled: true, bind_host: "192.168.10.8", url: "http://192.168.10.8:8000" };
function response(body: unknown, status = 200) { return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } }); }

describe("LAN access", () => {
  it("shows an actionable build instruction when the local frontend is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => String(input) === "/api/lan/status"
      ? response(inactive)
      : response({ error: { code: "lan_frontend_build_required", message: "需要先构建 Hard 前端：pnpm --dir apps/web build。" } }, 400)));
    const wrapper = mount(LanAccess);
    await vi.waitFor(() => expect((wrapper.get("select").element as HTMLSelectElement).value).toBe("192.168.10.8"));
    await wrapper.get('input[aria-label="我已理解局域网访问风险"]').setValue(true);
    await wrapper.get("button").trigger("click");
    await vi.waitFor(() => expect(wrapper.text()).toContain("pnpm --dir apps/web build"));
  });

  it("enables and then stops LAN access through the API", async () => {
    let status: typeof inactive | typeof active = inactive;
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (String(input) === "/api/lan/status") return response(status);
      if (init?.method === "POST") { status = active; return response(status); }
      if (init?.method === "DELETE") { status = inactive; return response(status); }
      throw new Error("unexpected request");
    }));
    const wrapper = mount(LanAccess);
    await vi.waitFor(() => expect((wrapper.get("select").element as HTMLSelectElement).value).toBe("192.168.10.8"));
    await wrapper.get('input[aria-label="我已理解局域网访问风险"]').setValue(true);
    await wrapper.get("button").trigger("click");
    await vi.waitFor(() => expect(wrapper.text()).toContain("http://192.168.10.8:8000"));
    await wrapper.get('button[type="button"]:last-of-type').trigger("click");
    await vi.waitFor(() => expect(wrapper.text()).not.toContain("http://192.168.10.8:8000"));
  });
});
