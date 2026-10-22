---
id: java-modern-ecosystem-java9-features
title: Java 9 新特性
concepts: [collections, functions]
objectives:
  - 掌握Java 9 新特性的核心概念与使用方式。
  - 用正常、边界和失败输入验证Java 9 新特性。
prerequisites: [java-modern-ecosystem-java8-features]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java9-new-features.html
source_snapshot_date: 2026-08-23
---

# Java 9 新特性

Java 9 引入模块系统（Jigsaw）、List.of/Set.of/Map.of 工厂方法和私有接口方法，增强封装和不可变集合创建。

```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        List<String> list = List.of("a", "b", "c");
        System.out.println(list.size());
        System.out.println(list.get(0));
    }
}
```

List.of 创建不可变列表，不允许添加或修改元素。

```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Map<String, Integer> map = Map.of("x", 1, "y", 2);
        System.out.println(map.size());
        System.out.println(map.get("x"));
    }
}
```

Map.of 创建不可变映射，最多支持 10 对键值。

## 概念定义与适用场景

Java 9 新特性解决的是不可变集合创建和模块化封装的问题。List.of/Set.of/Map.of 提供简洁的不可变集合创建方式，模块系统控制包的可见性。

## 语法、API 与边界

本课使用 List.of 创建不可变集合处理逗号分隔输入。输入为逗号分隔字符串，输出为首元素。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要对 List.of 创建的集合调用 add（抛出 UnsupportedOperationException）。Map.of 最多 10 对键值。提交前应覆盖单元素、多元素和边界长度的处理。
