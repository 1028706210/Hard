---
id: java-oop-io-nio-files
title: NIO Files
concepts: [io, types]
objectives:
  - 掌握NIO Files的核心概念与使用方式。
  - 用正常、边界和失败输入验证NIO Files。
prerequisites: [java-oop-io-packages]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-nio-file.html
source_snapshot_date: 2026-08-23
---

# NIO Files

Java NIO 的 java.nio.file 包提供 Path 和 Files 类，以路径和文件属性操作为核心，替代旧的 java.io.File API。

```java
import java.nio.file.Path;
import java.nio.file.Paths;

public class Main {
    public static void main(String[] args) {
        Path p = Paths.get("a", "b", "c.txt");
        System.out.println(p);
        System.out.println(p.getFileName());
    }
}

```

Paths.get 拼接路径组件，toString 输出跨平台路径字符串。

```java
import java.nio.file.Path;

public class Main {
    public static void main(String[] args) {
        Path p = Path.of("test.txt");
        String name = p.getFileName().toString();
        int dot = name.lastIndexOf('.');
        System.out.println(dot > 0 ? name.substring(dot + 1) : "none");
    }
}

```

从文件名提取扩展名需要处理无扩展名的边界情况。

## 概念定义与适用场景

NIO Files 解决的是跨平台文件路径操作与属性查询的问题。Path 类提供不可变的路径抽象，Files 类提供文件读写和属性操作。

## 语法、API 与边界

本课使用 Path API 处理路径字符串提取扩展名。输入为文件路径，输出为扩展名。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要混用 java.io.File 和 java.nio.file.Path。文件名可能没有扩展名，需要边界处理。提交前应覆盖有扩展名、无扩展名和多级路径的处理。
