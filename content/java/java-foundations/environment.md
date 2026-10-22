---
id: java-foundations-environment
title: Java 开发环境配置
concepts: [variables, control-flow]
objectives:
  - 解释JDK、javac 与 java 工具链在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 开发环境配置。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-environment-setup.html
source_snapshot_date: 2026-08-23
---

# Java 开发环境配置

## 概念定义与适用场景

javac 编译源文件，java 启动程序，两者应来自预期工具链。本题只是读取版本记录；真实安装与路径核对仍需在用户环境检查，不能靠打印版本文本证明。

## 语法、API 与边界

读取一个1到99的整数major，表示提供的JDK主版本记录。输出 major >= 17 的布尔值（true/false）；非整数、空输入或越界无输出，退出码1。只判断记录，不安装软件、不修改PATH，也不证明本机配置。支架已验证n。

```java
import java.nio.charset.StandardCharsets;
public class Main {

    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        long n;
        try { n = Long.parseLong(text); } catch (NumberFormatException error) { System.exit(1); return; }
        if (n < 1 || n > 99) { System.exit(1); return; }
        System.out.println(n >= 17);
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## 检查记录不能替代检查本机

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
int recordedMajor = 11;
boolean supported = recordedMajor >= 17;
System.out.println(supported); // false
```
