---
id: java-foundations-basic-syntax
title: Java 基础语法
concepts: [variables, control-flow]
objectives:
  - 解释类、main 方法和语句在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 基础语法。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-basic-syntax.html
source_snapshot_date: 2026-08-23
---

# Java 基础语法

## 概念定义与适用场景

语句位于方法体内，变量声明需要类型，语句以分号结束。起始代码提供真正换行的可编译类框架，保留大括号配对，只补齐本课计算。

## 语法、API 与边界

读取一个-1000000到1000000的整数n，在main中声明局部变量result为n加1并输出。零和负数有效；越界、非整数或空输入无输出，退出码1。支架提供合法n，请补齐声明和输出语句。

```java
import java.nio.charset.StandardCharsets;
public class Main {

    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        long n;
        try { n = Long.parseLong(text); } catch (NumberFormatException error) { System.exit(1); return; }
        if (n < -1000000 || n > 1000000) { System.exit(1); return; }
        long result = n + 1;
        System.out.println(result);
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## 变量初始化与输出顺序

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
int value = 0;
value = value + 1;
System.out.println(value); // 1
```
