---
id: java-core-api-string
title: String 类
concepts: [strings, operators]
objectives:
  - 掌握String 类的核心 API 与使用方式。
  - 用正常、边界和失败输入验证String 类。
prerequisites: [java-core-api-character]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-string.html
source_snapshot_date: 2026-08-23
---

# String 类

String 是 Java 中不可变的字符序列。它提供长度查询、子串提取、比较和连接等操作，是文本处理的基础类型。

```java
public class Main {
    public static void main(String[] args) {
        String s = "Hello";
        System.out.println(s.length());
        System.out.println(s.substring(1, 3));
    }
}

```

length 返回 UTF-16 代码单元数，不一定等于 Unicode 码点数或用户看到的字符数；substring(1,3) 提取代码单元索引 1 到 2 的子串。

```java
public class Main {
    public static void main(String[] args) {
        String a = "abc";
        String b = "abc";
        System.out.println(a.equals(b));
        System.out.println(a == b);
    }
}

```

equals 比较内容，== 比较引用。字符串常量池中相同字面量可能共享引用。

## 概念定义与适用场景

String 类解决的是不可变文本序列的存储与操作问题。它的不可变性使得字符串可以安全地在多线程间共享，但频繁拼接应使用 StringBuilder。

## 语法、API 与边界

本课使用 String 的实例方法处理文本输入。输入为字符串，输出为转换或查询结果。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要用 == 比较字符串内容，应使用 equals。substring 的 endIndex 是排他的。提交前应覆盖普通文本、空串和边界长度的处理。

本次事实核对：[Java 17 官方 API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/String.html)。
