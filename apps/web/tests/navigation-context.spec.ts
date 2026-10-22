import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it } from "vitest";
import { createMemoryHistory, createRouter } from "vue-router";
import { nextTick } from "vue";
import AppShell from "../src/app/AppShell.vue";

const mounted: ReturnType<typeof mount>[] = [];
afterEach(() => { mounted.splice(0).forEach(wrapper => wrapper.unmount()); });

async function renderShell(path: string) {
  const router = createRouter({ history: createMemoryHistory(), routes: [
    { path: "/lesson/:lessonId", component: { template: "<p>课时内容</p>" } },
    { path: "/assessment/:lessonId", component: { template: "<p>练习内容</p>" } },
    { path: "/:pathMatch(.*)*", component: { template: "<p>其他页面</p>" } },
  ] });
  await router.push(path);
  await router.isReady();
  const wrapper = mount(AppShell, { attachTo: document.body, global: { plugins: [router] } });
  mounted.push(wrapper);
  return { wrapper, router };
}

describe("learning navigation context", () => {
  it("retains the actual lesson in desktop and mobile shortcuts after opening another page", async () => {
    const { wrapper, router } = await renderShell("/lesson/java-core-api-methods");
    const linkFor = (scope: string, label: string) => wrapper.findAll(`${scope} a`).find(link => link.text() === label)!;
    expect(linkFor(".primary-nav", "当前课时").attributes("href")).toBe("/lesson/java-core-api-methods");
    expect(linkFor(".primary-nav", "练习评分").attributes("href")).toBe("/assessment/java-core-api-methods");
    await router.push("/review");
    await wrapper.get(".mobile-nav-trigger").trigger("click");
    expect(linkFor(".mobile-nav", "当前课时").attributes("href")).toBe("/lesson/java-core-api-methods");
    await router.push("/assessment/csharp-oop-classes");
    expect(linkFor(".primary-nav", "当前课时").attributes("href")).toBe("/lesson/csharp-oop-classes");
    expect(linkFor(".primary-nav", "练习评分").attributes("href")).toBe("/assessment/csharp-oop-classes");
  });

  it("returns keyboard focus to the mobile menu trigger after Escape", async () => {
    const { wrapper } = await renderShell("/");
    const trigger = wrapper.get(".mobile-nav-trigger");
    await trigger.trigger("click");
    (wrapper.get(".mobile-nav a").element as HTMLAnchorElement).focus();
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await nextTick();
    expect(trigger.attributes("aria-expanded")).toBe("false");
    expect(document.activeElement).toBe(trigger.element);
  });
});
