---
id: java-network-concurrency-networking
title: 网络编程
concepts: [io, web]
objectives:
  - 掌握网络编程的核心概念与使用方式。
  - 用正常、边界和失败输入验证网络编程。
prerequisites: [java-network-concurrency-serialization]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-networking.html
source_snapshot_date: 2026-08-23
---

# 网络编程

Java 网络编程通过 Socket 和 ServerSocket 实现 TCP 通信，URL 和 HttpURLConnection 处理 HTTP 请求。本课使用 mock 验证网络概念，不发起真实连接。

```java
import java.net.URL;

public class Main {
    public static void main(String[] args) throws Exception {
        URL url = new URL("http://example.com/path");
        System.out.println(url.getHost());
        System.out.println(url.getPath());
    }
}
```

URL 类解析地址，getHost 返回主机名，getPath 返回路径部分。

```java
import java.net.InetAddress;

public class Main {
    public static void main(String[] args) throws Exception {
        InetAddress addr = InetAddress.getByName("localhost");
        System.out.println(addr.getHostName());
        System.out.println(addr.isLoopbackAddress());
    }
}
```

InetAddress 表示 IP 地址，getByName 按主机名查找，isLoopbackAddress 判断回环。

## 概念定义与适用场景

网络编程解决的是跨进程通信与资源定位的问题。URL 类解析地址结构，Socket 类建立 TCP 连接，本课使用 mock 方式验证 URL 解析不发起真实连接。

## 语法、API 与边界

本课使用 URL 类解析地址处理输入。输入为 URL 字符串，输出为主机名。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要在练习中发起真实网络连接（使用 mock 验证解析逻辑）。URL 构造可能抛出 MalformedURLException。提交前应覆盖标准 URL、带路径 URL 和边界格式的解析。
