---
id: java-foundations-introduction
title: Java 简介
concepts: [variables, control-flow]
objectives:
  - 解释JVM、字节码和静态类型在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 简介。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-intro.html
source_snapshot_date: 2026-08-23
---

# Java 简介

## 概念定义与适用场景

Java 变量有声明类型。long 可以表达超出 int 范围的整数，但仍有上界，不能把静态类型误认为自动防止算术溢出。JVM 运行编译后的代码，而不是直接解释这段输入文本。

## 语法、API 与边界

读取一个 Java long 范围内的整数 n，声明 long next = n + 1 并输出。为避免溢出，n 等于 Long.MAX_VALUE 时拒绝；非法整数或空输入无输出，退出码1。支架提供 n 和边界检查，观察静态类型与计算结果。

```java
import java.nio.charset.StandardCharsets;
public class Main {

    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        long n;
        try { n = Long.parseLong(text); } catch (NumberFormatException error) { System.exit(1); return; }
        if (n == Long.MAX_VALUE) { System.exit(1); return; }
        long next = n + 1;
        System.out.println(next);
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## 提升运算范围前先选择类型

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
long count = 2147483647L;
System.out.println(count + 1); // 2147483648
```
