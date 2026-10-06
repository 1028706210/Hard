import { expect, test } from "@playwright/test";


test.beforeEach(async ({ page }) => {
  let enabled = false;
  const status = () => ({
    enabled,
    bind_host: enabled ? "192.168.10.8" : "127.0.0.1",
    port: 8000,
    url: enabled ? "http://192.168.10.8:8000" : null,
    interfaces: ["192.168.10.8"],
    warning: "同一网络设备可访问数据并运行代码。",
    firewall_preview: "New-NetFirewallRule -Profile Private",
    firewall_revoke_preview: "Remove-NetFirewallRule",
  });
  await page.route("**/api/v1/health/ready", (route) => route.fulfill({ json: { status: "ok", checks: {} } }));
  await page.route("**/api/progress/summary", (route) => route.fulfill({ json: { daily_goal: { target_minutes: 0, target_exercises: 0 }, streak_days: 0, due_review_count: 0, current_experience: 0, current_level: 1 } }));
  await page.route("**/api/lan/status", (route) => route.fulfill({ json: status() }));
  await page.route("**/api/lan/enable", (route) => {
    enabled = route.request().method() === "POST";
    return route.fulfill({ json: status() });
  });
});

test("LAN controls require an explicit warning acknowledgement and render a local URL QR without firewall execution", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/settings");
  await expect(page.getByText("同一网络设备可访问数据并运行代码")).toBeVisible();
  const enable = page.getByRole("button", { name: "启用局域网访问" });
  await expect(enable).toBeDisabled();
  await page.getByLabel("我已理解局域网访问风险").check();
  await expect(enable).toBeEnabled();
  await enable.click();
  await expect(page.getByText("http://192.168.10.8:8000")).toBeVisible();
  await expect(page.locator("svg[data-qr-code]")).toHaveAttribute("aria-label", "局域网地址二维码");
  await page.getByText("防火墙命令预览（未执行）").click();
  await expect(page.getByText("New-NetFirewallRule -Profile Private")).toBeVisible();
  await page.getByRole("button", { name: "停止局域网访问" }).click();
  await expect(page.getByText("http://192.168.10.8:8000")).toBeHidden();
  await expect(page.getByRole("button", { name: "启用局域网访问" })).toBeVisible();
  expect(await page.locator("html").evaluate((element) => element.scrollWidth <= window.innerWidth)).toBeTruthy();
});
