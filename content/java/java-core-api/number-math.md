---
id: java-core-api-number-math
title: Number 与 Math 类
concepts: [types, operators]
objectives:
  - 掌握Number 与 Math 类的核心 API 与使用方式。
  - 用正常、边界和失败输入验证Number 与 Math 类。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-number.html
source_snapshot_date: 2026-08-23
---

# Number 与 Math 类

Java 的 Math 类封装了常用数学运算。Number 是所有数值包装类的父类，提供基本类型与对象之间的转换桥梁。

```java
public class Main {
    public static void main(String[] args) {
        int a = 7, b = 3;
        System.out.println(Math.max(a, b));
        System.out.println(Math.abs(-5));
    }
}

```

Math.max 返回两个值中的较大者，Math.abs 返回绝对值。

```java
public class Main {
    public static void main(String[] args) {
        double r = 2.0;
        double area = Math.PI * r * r;
        System.out.println(Math.round(area));
    }
}

```

Math.PI 提供圆周率常量，Math.round 对浮点数四舍五入为最近整数。

## 概念定义与适用场景

Number 与 Math 解决的是数值存储与运算的问题。Number 类层次（Integer、Double 等）让基本类型可以在需要对象的场景中使用，Math 类提供静态方法完成超越运算。

## 语法、API 与边界

本课只使用 Math 类的静态方法和基本类型运算。输入为整数或浮点数文本，输出为计算结果。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要混淆整数除法与浮点除法（3/2 得 1，3.0/2 得 1.5）。提交前应覆盖正数、负数和零值的运算，确保 Math.round 的半数进位方向符合预期。
