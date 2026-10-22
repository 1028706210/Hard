---
id: java-core-api-scanner
title: Scanner 类
concepts: [io, functions]
objectives:
  - 掌握Scanner 类的核心 API 与使用方式。
  - 用正常、边界和失败输入验证Scanner 类。
prerequisites: [java-core-api-constructors]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-scanner-class.html
source_snapshot_date: 2026-08-23
---

# Scanner 类

Scanner 是 Java 中解析输入文本的工具类。它通过分隔符将输入流拆分为 token，支持按类型读取整数、浮点数和字符串。

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner("10 20 30");
        int sum = 0;
        while (sc.hasNextInt()) sum += sc.nextInt();
        System.out.println(sum);
    }
}

```

Scanner 从字符串创建，hasNextInt 判断是否有整数，nextInt 读取并消费。

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner("hello world");
        System.out.println(sc.next());
        System.out.println(sc.next());
    }
}

```

next 读取下一个 token（以空白分隔），连续调用依次消费后续 token。

## 概念定义与适用场景

Scanner 解决的是从输入流或字符串中按类型解析 token 的问题。它提供 hasNext/next 系列方法，支持整数、浮点数和字符串的逐个读取。

## 语法、API 与边界

本课使用 Scanner 解析多行混合输入。输入为多行 token，输出为统计或转换结果。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要忘记关闭 Scanner 或使用 try-with-resources。hasNextInt 防止类型不匹配异常。提交前应覆盖整数、非整数和空输入的读取行为。
