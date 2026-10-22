---
id: java-core-api-methods
title: 方法
concepts: [functions, operators]
objectives:
  - 掌握方法的核心 API 与使用方式。
  - 用正常、边界和失败输入验证方法。
prerequisites: [java-core-api-regex]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-methods.html
source_snapshot_date: 2026-08-23
---

# 方法

方法是 Java 中可复用的代码块。它通过参数接收输入，通过返回值输出结果，支持重载和递归调用。

```java
public class Main {
    static int add(int a, int b) {
        return a + b;
    }
    public static void main(String[] args) {
        System.out.println(add(3, 4));
    }
}

```

static 方法可直接通过类名调用，参数传递值，return 返回结果。

```java
public class Main {
    static int gcd(int a, int b) {
        if (b == 0) return a;
        return gcd(b, a % b);
    }
    public static void main(String[] args) {
        System.out.println(gcd(12, 18));
    }
}

```

递归方法调用自身，需要明确的终止条件防止无限循环。

## 概念定义与适用场景

方法解决的是代码复用与逻辑封装的问题。它通过参数和返回值定义输入输出契约，通过访问修饰符控制可见性。

## 语法、API 与边界

本课使用 static 方法定义计算逻辑并调用。输入为方法参数，输出为返回值。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要忽略方法的返回值。递归方法必须有终止条件。提交前应覆盖正常参数、边界值和非法输入的方法行为。
