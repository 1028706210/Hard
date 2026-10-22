---
id: java-foundations-operators
title: Java 运算符
concepts: [variables, control-flow]
objectives:
  - 解释算术、比较、逻辑与短路在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 运算符。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-operators.html
source_snapshot_date: 2026-08-23
---

# Java 运算符

## 概念定义与适用场景

Java整数余数的符号随被除数，与部分语言的取模规则不同。除数为零必须在计算前拒绝；&&与||可以短路，但要仔细确认条件覆盖范围。

## 语法、API 与边界

读取两个-1000000到1000000的整数left、right，right不能为0。输出Java的left % right结果，保留Java余数符号语义，例如-7 3输出-1。非法输入无输出，退出码1。支架已校验操作数。

```java
import java.nio.charset.StandardCharsets;
public class Main {

    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        String[] parts = text.split("\s+");
        long left, right;
        try {
            if (parts.length != 2) throw new NumberFormatException();
            left = Long.parseLong(parts[0]); right = Long.parseLong(parts[1]);
        } catch (NumberFormatException error) { System.exit(1); return; }
        if (Math.abs(left) > 1000000 || Math.abs(right) > 1000000 || left == Long.MIN_VALUE || right == Long.MIN_VALUE || right == 0) { System.exit(1); return; }
        System.out.println(left % right);
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## 余数符号随被除数

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
System.out.println(-7 % 3); // -1
System.out.println(7 % -3); // 1
```
