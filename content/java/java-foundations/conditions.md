---
id: java-foundations-conditions
title: Java 条件语句
concepts: [variables, control-flow]
objectives:
  - 解释if/else 分支与兜底路径在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 条件语句。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-if-else-switch.html
source_snapshot_date: 2026-08-23
---

# Java 条件语句

## 概念定义与适用场景

if和else构成互斥分支，必须明确等于阈值归到哪一边。输入范围不合法与合法但未通过是不同情况，不能统一静默退出。

## 语法、API 与边界

读取0到100整数成绩n，if/else在n>=60时输出pass，否则输出retry。端点0、60、100均有效；非法输入无输出，退出码1。支架已校验n。

```java
import java.nio.charset.StandardCharsets;
public class Main {

    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        long n;
        try { n = Long.parseLong(text); } catch (NumberFormatException error) { System.exit(1); return; }
        if (n < 0 || n > 100) { System.exit(1); return; }
        if (n >= 60) { System.out.println("pass"); } else { System.out.println("retry"); }
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## 临界值必须归入明确分支

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
int score = 60;
System.out.println(score >= 60 ? "pass" : "retry"); // pass
```
