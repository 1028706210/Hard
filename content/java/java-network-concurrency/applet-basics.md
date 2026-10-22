---
id: java-network-concurrency-applet-basics
title: Applet 基础
concepts: [io, types]
objectives:
  - 掌握Applet 基础的核心概念与使用方式。
  - 用正常、边界和失败输入验证Applet 基础。
prerequisites: [java-network-concurrency-multithreading]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-applet-basics.html
source_snapshot_date: 2026-08-23
---

# Applet 基础

Applet 是 Java 的浏览器嵌入程序技术（已弃用）。其生命周期由 init、start、stop 和 destroy 四个阶段组成。本课作为历史知识讲解生命周期概念，不要求浏览器运行。

```java
abstract class Applet {
    void init() { System.out.println("init"); }
    void start() { System.out.println("start"); }
    void stop() { System.out.println("stop"); }
    void destroy() { System.out.println("destroy"); }
}
public class Main {
    public static void main(String[] args) {
        Applet a = new Applet() {};
        a.init(); a.start(); a.stop(); a.destroy();
    }
}
```

Applet 生命周期按 init→start→stop→destroy 顺序执行，本课用抽象类模拟。

```java
public class Main {
    public static void main(String[] args) {
        String[] stages = {"init", "start", "stop", "destroy"};
        for (String s : stages) System.out.println(s);
    }
}
```

生命周期阶段是固定的有序序列，遍历输出展示完整流程。

## 概念定义与适用场景

Applet 生命周期解决的是浏览器嵌入程序的阶段管理问题。它通过 init、start、stop、destroy 四个回调定义程序各阶段行为。Applet 已被弃用，作为历史知识学习。

## 语法、API 与边界

本课使用字符串映射模拟生命周期阶段转换。输入为当前阶段名，输出下一阶段名。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

Applet 已弃用，不要在新项目中使用。本课仅学习生命周期概念。提交前应覆盖各阶段转换和边界输入的处理。
