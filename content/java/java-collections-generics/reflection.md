---
id: java-collections-generics-reflection
title: 反射
concepts: [classes, tooling]
objectives:
  - 掌握反射的核心概念与使用方式。
  - 用正常、边界和失败输入验证反射。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-reflection.html
source_snapshot_date: 2026-08-23
---

# 反射

反射允许程序在运行时检查和操作类、方法和字段。Class 对象是反射的入口，提供类名、方法和字段信息。

```java
public class Main {
    public static void main(String[] args) throws Exception {
        Class<?> c = Class.forName("java.lang.String");
        System.out.println(c.getSimpleName());
    }
}
```

Class.forName 按全名加载类，getSimpleName 返回不含包名的类名。

```java
import java.lang.reflect.Method;

public class Main {
    public static void main(String[] args) throws Exception {
        Method[] ms = String.class.getMethods();
        System.out.println(ms.length > 0);
    }
}
```

getMethods 返回类的所有公共方法，可遍历检查方法签名。

## 概念定义与适用场景

反射解决的是运行时类型检查与动态调用的问题。它通过 Class 对象获取类的结构信息，支持动态创建实例和调用方法。

## 语法、API 与边界

本课使用 Class.forName 获取类信息处理类名输入。输入为全限定类名，输出为简单类名。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要在性能关键路径用反射（比直接调用慢）。反射会绕过编译时类型检查。提交前应覆盖已知类、未知类和边界输入的反射行为。
