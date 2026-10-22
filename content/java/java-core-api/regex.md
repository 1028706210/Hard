---
id: java-core-api-regex
title: 正则表达式
concepts: [strings, security]
objectives:
  - 掌握正则表达式的核心 API 与使用方式。
  - 用正常、边界和失败输入验证正则表达式。
prerequisites: [java-core-api-date-time]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-regular-expressions.html
source_snapshot_date: 2026-08-23
---

# 正则表达式

Java 通过 Pattern 和 Matcher 类支持正则表达式。Pattern 编译正则模式，Matcher 对输入文本进行匹配和提取。

```java
import java.util.regex.*;

public class Main {
    public static void main(String[] args) {
        Pattern p = Pattern.compile("\\d+");
        Matcher m = p.matcher("abc123");
        System.out.println(m.find());
    }
}

```

Pattern.compile 编译模式，Matcher.find 查找下一个匹配。

```java
import java.util.regex.*;

public class Main {
    public static void main(String[] args) {
        boolean r = "test@example.com".matches("[a-z]+@[a-z]+\\.[a-z]+");
        System.out.println(r);
    }
}

```

String.matches 直接对字符串进行完整匹配，返回布尔值。

## 概念定义与适用场景

正则表达式解决的是文本模式匹配与提取的问题。Pattern 编译后的模式可复用，Matcher 提供匹配、查找和分组操作。

## 语法、API 与边界

本课使用 Pattern 和 String.matches 处理文本匹配输入。输入为字符串，输出为匹配判断结果。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要在循环中反复 compile 同一模式，应提取为常量。注意 Java 字符串中反斜杠需要双重转义。提交前应覆盖匹配、不匹配和边界长度的文本。
