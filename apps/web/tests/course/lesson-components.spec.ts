import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import LessonContent from "../../src/features/course/LessonContent.vue";
import LessonNav from "../../src/features/course/LessonNav.vue";


describe("lesson workspace components", () => {
  it("links to actual article sections and refreshes them when the lesson changes", async () => {
    const lesson = { id: "sections", title: "课时标题", rendered_html: "<h1>课时标题</h1><p>导言</p><h2>开始</h2><p>正文</p><h3>开始</h3>", source_url: "https://www.runoob.com/python3/", source_snapshot_date: "2026-08-23" };
    const content = mount(LessonContent, { props: { lesson } });
    const links = content.findAll('nav[aria-label="本课章节"] a');
    expect(links.map(link => link.text())).toEqual(["开始", "开始"]);
    expect(new Set(links.map(link => link.attributes("href"))).size).toBe(2);
    for (const link of links) expect(content.find(link.attributes("href")!).exists()).toBe(true);
    expect(content.findAll("h1")).toHaveLength(1);

    await content.setProps({ lesson: { ...lesson, id: "simple", rendered_html: "<p>简短正文</p>" } });
    expect(content.find('nav[aria-label="本课章节"]').exists()).toBe(false);
    expect(content.get(".lesson-content__body").text()).toBe("简短正文");
  });

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
