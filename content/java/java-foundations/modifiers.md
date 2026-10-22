---
id: java-foundations-modifiers
title: Java 修饰符
concepts: [variables, control-flow]
objectives:
  - 解释public、private、static 与访问边界在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 修饰符。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-modifier-types.html
source_snapshot_date: 2026-08-23
---

# Java 修饰符

## 概念定义与适用场景

private收窄字段访问范围，public暴露明确接口，final禁止重新赋值，static表示成员属于类。它们不是同一个维度；getter可表达受控读取，但不自动保证对象线程安全。

## 语法、API 与边界

读取一个long整数n，使用具有private final value字段和public getValue()方法的Box对象保存并输出它。非法整数或空输入无输出，退出码1。Box骨架已提供，使用getter读取，main保持public static。输出测试不证明所有访问控制写法均正确。

```java
import java.nio.charset.StandardCharsets;
public class Main {
    static class Box { private final long value; Box(long value) { this.value = value; } public long getValue() { return value; } }
    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        long n;
        try { n = Long.parseLong(text); } catch (NumberFormatException error) { System.exit(1); return; }
        Box box = new Box(n);
        System.out.println(box.getValue());
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## 公开行为与内部状态分开

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
class Box {
    private final long value;
    Box(long value) { this.value = value; }
    public long getValue() { return value; }
}
```
