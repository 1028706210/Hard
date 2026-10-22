---
id: java-core-api-date-time
title: 日期时间
concepts: [types, io]
objectives:
  - 掌握日期时间的核心 API 与使用方式。
  - 用正常、边界和失败输入验证日期时间。
prerequisites: [java-core-api-arrays]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-date-time.html
source_snapshot_date: 2026-08-23
---

# 日期时间

Java 的 java.time 包提供 LocalDate、LocalTime 和 LocalDateTime 等不可变日期时间类，替代了旧的 Date 和 Calendar。

```java
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class Main {
    public static void main(String[] args) {
        LocalDate d = LocalDate.of(2026, 1, 15);
        System.out.println(d.plusDays(1));
    }
}

```

LocalDate.of 创建日期，plusDays 返回加天数后的新日期对象。

```java
import java.time.LocalDate;

public class Main {
    public static void main(String[] args) {
        LocalDate d = LocalDate.parse("2026-12-31");
        System.out.println(d.plusDays(1).getYear());
    }
}

```

parse 从 ISO 格式字符串创建日期，跨年加天数自动进位年份。

## 概念定义与适用场景

日期时间类解决的是日期的计算与格式化问题。LocalDate 等类不可变且线程安全，加减天数返回新对象。

## 语法、API 与边界

本课使用 LocalDate 的 parse 和 plusDays 方法处理日期输入。输入为 ISO 格式日期字符串，输出为计算后的日期。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

新代码通常优先选择 java.time；JDK 17 并未将 Date 和 Calendar 整个类标为弃用，Date 的部分旧方法已弃用。月份在旧 Calendar 中从 0 开始，但 LocalDate 中从 1 开始。提交前应覆盖跨月、跨年和闰年的日期计算。

本次事实核对：[Java 17 官方 API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Date.html)。
