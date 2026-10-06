import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import LessonContent from "../../src/features/course/LessonContent.vue";
import LessonNav from "../../src/features/course/LessonNav.vue";


describe("lesson workspace components", () => {
  it("marks locked lessons in navigation and renders the structured source link", () => {
    const navigation = mount(LessonNav, {
      props: {
        modules: [{ id: "python-foundations", title: "Python 基础", prerequisites: [], lessons: [
          { id: "hello", title: "Hello", locked: false },
          { id: "output", title: "输出", locked: true },
        ] }],
        open: true,
      },
      global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } },
    });
    const content = mount(LessonContent, {
      props: {
        lesson: { id: "hello", title: "Hello", rendered_html: "<p>正文</p>", source_url: "https://www.runoob.com/python3/python3-hello-world.html", source_snapshot_date: "2026-08-23" },
      },
    });

    expect(navigation.text()).toContain("完成前置后解锁");
    expect(navigation.find("button[disabled]").text()).toContain("输出");
    expect(content.get('a[rel="noreferrer"]').attributes("href")).toBe("https://www.runoob.com/python3/python3-hello-world.html");
  });
});
