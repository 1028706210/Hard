import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import DataManagement from "../../src/features/settings/DataManagement.vue";


function response(body: unknown) {
  return new Response(JSON.stringify(body), { headers: { "content-type": "application/json" } });
}

describe("data management", () => {
  it("exports a local archive and uploads an explicit selected archive without implying D-drive hardware safety", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (String(input) === "/api/backup/export") {
        expect(init?.method).toBe("POST");
        expect(init?.headers).toMatchObject({ "Idempotency-Key": expect.any(String) });
        return response({ archive_name: "hard-export-test.zip", content_version: "sha256-content" });
      }
      if (String(input) === "/api/backup/import") {
        expect(init?.method).toBe("POST");
        expect(init?.headers).toMatchObject({ "X-Archive-Name": "hard-export-test.zip", "Idempotency-Key": expect.any(String) });
        expect(init?.body).toBeInstanceOf(File);
        return response({ content_version: "sha256-content" });
      }
      throw new Error(`unexpected ${String(input)}`);
    });
    vi.stubGlobal("fetch", fetchMock);
    const wrapper = mount(DataManagement);

    await wrapper.get("button").trigger("click");
    await vi.waitFor(() => expect(wrapper.get("[data-export-name]").text()).toContain("hard-export-test.zip"));
    expect(wrapper.text()).toContain("同一 D 盘备份不能防止硬盘损坏");

    const file = new File(["archive"], "hard-export-test.zip", { type: "application/zip" });
    const input = wrapper.get('input[type="file"]');
    Object.defineProperty(input.element, "files", { value: [file] });
    await input.trigger("change");
    await wrapper.get('[data-import-archive]').trigger("click");
    await vi.waitFor(() => expect(wrapper.text()).toContain("导入完成"));
  });
});
