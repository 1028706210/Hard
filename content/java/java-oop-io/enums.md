---
id: java-oop-io-enums
title: 枚举
concepts: [types, classes]
objectives:
  - 掌握枚举的核心概念与使用方式。
  - 用正常、边界和失败输入验证枚举。
prerequisites: [java-oop-io-interfaces]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-enum.html
source_snapshot_date: 2026-08-23
---

# 枚举

枚举用 enum 定义，是一组命名常量的固定集合。Java 枚举是特殊的类，可以包含字段、方法和构造方法。

```java
enum Color {
    RED, GREEN, BLUE;
    int code() { return ordinal() + 1; }
}
public class Main {
    public static void main(String[] args) {
        System.out.println(Color.RED.code());
        System.out.println(Color.valueOf("GREEN"));
    }
}

```

ordinal 返回声明顺序索引，valueOf 按名称查找枚举常量。

```java
enum Level {
    LOW(1), MID(2), HIGH(3);
    final int v;
    Level(int v) { this.v = v; }
}
public class Main {
    public static void main(String[] args) {
        for (Level l : Level.values()) System.out.println(l + ":" + l.v);
    }
}

```

枚举可带字段和构造方法，values 返回所有常量的有序数组。

## 概念定义与适用场景

枚举解决的是固定值集合的类型安全表示问题。它比常量更安全——编译器检查枚举值有效性，且支持方法和字段扩展。

## 语法、API 与边界

本课使用枚举类型处理颜色名称到数值的映射。输入为颜色名称，输出为对应数值。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要用 int 常量替代枚举（失去类型安全）。枚举构造方法总是私有的。提交前应覆盖有效值、无效值和大小写敏感的处理。
