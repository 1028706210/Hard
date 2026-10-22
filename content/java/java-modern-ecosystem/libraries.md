---
id: java-modern-ecosystem-libraries
title: 常用类库
concepts: [packages, tooling]
objectives:
  - 掌握常用类库的核心概念与使用方式。
  - 用正常、边界和失败输入验证常用类库。
prerequisites: [java-modern-ecosystem-mysql-connect]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-libs.html
source_snapshot_date: 2026-08-23
---

# 常用类库

Java 生态拥有丰富的开源类库：Jackson 处理 JSON、Guava 提供工具增强、Log4j 记录日志、JUnit 单元测试等。

```java
public class Main {
    public static void main(String[] args) {
        String[] libs = {"Jackson", "Guava", "Log4j", "JUnit"};
        for (String lib : libs) System.out.println(lib);
    }
}
```

常用 Java 类库覆盖 JSON、工具、日志和测试等不同领域。

```java
public class Main {
    public static void main(String[] args) {
        String lib = "Jackson";
        String category = switch (lib) {
            case "Jackson" -> "JSON";
            case "Guava" -> "Utility";
            case "Log4j" -> "Logging";
            default -> "Other";
        };
        System.out.println(category);
    }
}
```

switch 表达式按库名返回分类，Java 14+ 支持 arrow 语法。

## 概念定义与适用场景

常用类库解决的是 JSON 处理、工具增强、日志记录和测试自动化的问题。选择成熟类库而非重复造轮子是工程效率的关键。

## 语法、API 与边界

本课使用 switch 表达式按库名分类处理输入。输入为库名，输出为分类。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要引入过多依赖（增加维护成本）。选择类库应考虑活跃度、社区支持和许可证。提交前应覆盖已知库、未知库和边界输入的分类。
