---
id: java-oop-io-files-io
title: Stream/File/IO
concepts: [io, types]
objectives:
  - 掌握Stream/File/IO的核心概念与使用方式。
  - 用正常、边界和失败输入验证Stream/File/IO。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-files-io.html
source_snapshot_date: 2026-08-23
---

# Stream/File/IO

Java 的 java.nio.file 包提供 Path 和 Files 类处理文件路径与操作，替代了旧的 File 类。

```java
import java.nio.file.Path;

public class Main {
    public static void main(String[] args) {
        Path p = Path.of("a/b.txt");
        System.out.println(p.getFileName());
    }
}

```

Path.of 创建路径对象，getFileName 返回文件名部分。

```java
import java.nio.file.Path;

public class Main {
    public static void main(String[] args) {
        Path p = Path.of("a/b/c.txt");
        System.out.println(p.getParent());
        System.out.println(p.getNameCount());
    }
}

```

getParent 返回父目录，getNameCount 返回路径组件数。

## 概念定义与适用场景

文件 IO 解决的是路径解析与文件操作的问题。Path 类提供跨平台的路径操作，Files 类提供读写和属性查询。

## 语法、API 与边界

本课使用 Path API 处理路径字符串输入。输入为文件路径，输出为路径组件。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要混淆 Path 与旧的 File 类。路径分隔符跨平台不同，使用 Path 自动处理。提交前应覆盖简单路径、嵌套路径和带扩展名的处理。
