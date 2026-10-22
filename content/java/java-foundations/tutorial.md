---
id: java-foundations-tutorial
title: Java 教程
concepts: [variables, control-flow]
objectives:
  - 解释程序入口、编译和运行在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 教程。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-tutorial.html
source_snapshot_date: 2026-08-23
---

# Java 教程

## 概念定义与适用场景

Main.java 编译成字节码，再由 JVM 调用 main。类名、方法签名与语句结尾分号有明确作用；看到输出说明这次代码被执行，不代表所有环境配置都已验证。

## 语法、API 与边界

在 public class Main 的 main 中读取一段名称，使用已提供 text（去除首尾 ASCII 控制空白），输出 Hello, 后接一个空格和名称。内部空格与中文保留；空输入无输出，退出码1。补齐输出语句，不要打印固定样例。

```java
import java.nio.charset.StandardCharsets;
public class Main {

    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        if (text.isEmpty()) { System.exit(1); return; }
        System.out.println("Hello, " + text);
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## 一次输入与固定输出不同

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
String name = "Ada";
System.out.println("Hello, " + name); // Hello, Ada
```
