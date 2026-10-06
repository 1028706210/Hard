import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import SettingsPage from "../../src/features/settings/SettingsPage.vue";


function response(body: unknown) {
  return new Response(JSON.stringify(body), { headers: { "content-type": "application/json" } });
}

describe("settings page", () => {
  it("shows D-drive health and paths, honest phone and backup risk, and persists a daily goal", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === "/api/v1/health/ready") return response({ status: "ok", checks: { database: { healthy: true, path: "D:/projects/1/Hard-task1/data/hard.db" }, python: { healthy: true, path: "D:/DevTools/python/python.exe" }, java: { healthy: false, path: "D:/DevTools/java/bin/java.exe" } } });
      if (url === "/api/progress/summary") return response({ daily_goal: { target_minutes: 25, target_exercises: 2 }, streak_days: 0, due_review_count: 0, current_experience: 0, current_level: 1 });
      if (url === "/api/progress/daily-goal") {
        expect(init?.method).toBe("PUT");
        expect(init?.headers).toMatchObject({ "Idempotency-Key": expect.any(String) });
        expect(init?.body).toBe(JSON.stringify({ target_minutes: 30, target_exercises: 3 }));
        return response({ date: "2026-08-25", configured: true, target_minutes: 30, target_exercises: 3 });
      }
      throw new Error(`unexpected ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const wrapper = mount(SettingsPage);
    await vi.waitFor(() => expect(wrapper.text()).toContain("D:/DevTools/python/python.exe"));
    expect(wrapper.text()).toContain("同一 D 盘备份不能防止硬盘损坏");
    expect(wrapper.text()).toContain("同一网络设备可访问数据并运行代码");
    expect(wrapper.text()).toContain("需要注意");
    await wrapper.get('input[aria-label="每日学习分钟"]').setValue("30");
    await wrapper.get('input[aria-label="每日练习数量"]').setValue("3");
    await wrapper.get('form').trigger("submit.prevent");
    await vi.waitFor(() => expect(wrapper.text()).toContain("目标已保存"));
  });
});
