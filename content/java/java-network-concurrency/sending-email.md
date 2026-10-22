---
id: java-network-concurrency-sending-email
title: 发送邮件
concepts: [web, security]
objectives:
  - 掌握发送邮件的核心概念与使用方式。
  - 用正常、边界和失败输入验证发送邮件。
prerequisites: [java-network-concurrency-networking]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-sending-email.html
source_snapshot_date: 2026-08-23
---

# 发送邮件

Java 通过 javax.mail 或 Jakarta Mail 实现 SMTP 邮件发送。本课使用 mock 验证邮件地址格式，不连接 SMTP 服务器。

```java
public class Main {
    public static void main(String[] args) {
        String email = "test@example.com";
        boolean valid = email.matches("[a-z]+@[a-z]+\\.[a-z]+");
        System.out.println(valid);
    }
}
```

用正则验证邮件地址格式，不连接服务器，仅检查结构。

```java
public class Main {
    public static void main(String[] args) {
        String[] parts = "user@domain.com".split("@");
        System.out.println(parts[0]);
        System.out.println(parts[1]);
    }
}
```

邮件地址用 @ 分隔用户名和域名，split 提取各部分。

## 概念定义与适用场景

邮件发送解决的是异步消息传递的问题。SMTP 协议定义发送流程，本课使用 mock 方式验证邮件地址格式而不连接 SMTP 服务器。

## 语法、API 与边界

本课使用正则和字符串操作验证邮件格式。输入为邮件地址，输出为 VALID 或 INVALID。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要在练习中连接真实 SMTP 服务器。邮件验证应检查格式而非确认可达性。提交前应覆盖标准格式、缺少 @ 和边界长度的验证。
