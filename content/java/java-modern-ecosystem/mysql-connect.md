---
id: java-modern-ecosystem-mysql-connect
title: MySQL 连接
concepts: [databases, io]
objectives:
  - 掌握MySQL 连接的核心概念与使用方式。
  - 用正常、边界和失败输入验证MySQL 连接。
prerequisites: [java-modern-ecosystem-java9-features]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-mysql-connect.html
source_snapshot_date: 2026-08-23
---

# MySQL 连接

Java 通过 JDBC API 连接 MySQL 数据库。本课使用 mock 验证 JDBC URL 格式和 SQL 语句结构，不连接真实数据库。

```java
public class Main {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/test";
        System.out.println(url.startsWith("jdbc:mysql://"));
    }
}
```

JDBC URL 以 jdbc:mysql:// 开头，包含主机、端口和数据库名。

```java
public class Main {
    public static void main(String[] args) {
        String sql = "SELECT * FROM users WHERE id = ?";
        System.out.println(sql.contains("?"));
        System.out.println(sql.toUpperCase().startsWith("SELECT"));
    }
}
```

参数化 SQL 用 ? 占位符防止注入，SQL 语句类型通过关键字判断。

## 概念定义与适用场景

MySQL 连接解决的是 Java 程序与关系数据库交互的问题。JDBC 提供统一 API，本课使用 mock 验证 URL 和 SQL 格式而不连接真实数据库。

## 语法、API 与边界

本课使用字符串操作验证 JDBC URL 格式处理输入。输入为 URL 字符串，输出为 VALID 或 INVALID。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要在练习中连接真实数据库（使用 mock 验证格式）。SQL 查询应使用参数化（?占位符）防止注入。提交前应覆盖标准 URL、缺少前缀和边界格式的验证。
