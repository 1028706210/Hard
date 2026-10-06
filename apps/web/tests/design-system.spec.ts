import { createMemoryHistory } from "vue-router";
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";

import App from "../src/App.vue";
import { createHardRouter, destinations } from "../src/app/router";


async function mountAt(path: string) {
  const router = createHardRouter(createMemoryHistory());
  await router.push(path);
  await router.isReady();
  return mount(App, { global: { plugins: [router] } });
}


describe("Hard design system shell", () => {
  it("exposes all eight destinations in semantic desktop navigation with the current page", async () => {
    const wrapper = await mountAt("/review");
    const links = wrapper.get(".primary-nav").findAll("a");

    expect(links).toHaveLength(destinations.length);
    expect(links.map((link) => link.text())).toEqual(destinations.map((destination) => destination.label));
    expect(wrapper.get('.primary-nav a[aria-current="page"]').text()).toBe("复习");
  });

  it("offers a keyboard-addressable mobile menu with an explicit open state", async () => {
    const wrapper = await mountAt("/");
    const trigger = wrapper.get('button[aria-controls="mobile-navigation"]');

    expect(trigger.attributes("aria-expanded")).toBe("false");
    await trigger.trigger("click");
    expect(trigger.attributes("aria-expanded")).toBe("true");
    expect(wrapper.get("#mobile-navigation").findAll("a")).toHaveLength(destinations.length);
  });
});
