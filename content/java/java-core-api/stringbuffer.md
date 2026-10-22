---
id: java-core-api-stringbuffer
title: StringBuffer 类
concepts: [strings, collections]
objectives:
  - 掌握StringBuffer 类的核心 API 与使用方式。
  - 用正常、边界和失败输入验证StringBuffer 类。
prerequisites: [java-core-api-string]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-stringbuffer.html
source_snapshot_date: 2026-08-23
---

# StringBuffer 类

StringBuffer 是可变字符序列，适合频繁拼接和修改操作。与不可变的 String 不同，它提供 append、insert 和 reverse 等就地修改方法。

```java
public class Main {
    public static void main(String[] args) {
        StringBuffer sb = new StringBuffer("Hello");
        sb.append(" World");
        System.out.println(sb);
    }
}

```

append 在末尾追加文本，直接修改原对象而非创建新字符串。

```java
public class Main {
    public static void main(String[] args) {
        StringBuffer sb = new StringBuffer("abc");
        sb.reverse();
        System.out.println(sb);
        System.out.println(sb.charAt(0));
    }
}

```

reverse 原地反转字符序列，charAt 按索引访问单个字符。

## 概念定义与适用场景

StringBuffer 解决的是可变文本序列的构建与修改问题。它提供线程安全的就地操作，适合循环拼接和动态构建文本。

## 语法、API 与边界

本课使用 StringBuffer 的 append 和 reverse 方法处理多行输入。输入为多行文本，输出为拼接或反转结果。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要在单线程场景过度使用 StringBuffer，StringBuilder 更高效。提交前应覆盖单行、多行和空行的拼接操作。
