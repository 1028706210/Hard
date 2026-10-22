---
id: java-oop-io-packages
title: Package
concepts: [classes, tooling]
objectives:
  - 掌握Package的核心概念与使用方式。
  - 用正常、边界和失败输入验证Package。
prerequisites: [java-oop-io-enums]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-package.html
source_snapshot_date: 2026-08-23
---

# Package

包（package）是 Java 中组织类的命名空间。它通过点分层级路径避免类名冲突，配合 import 导入其他包的类。

```java
package com.example;

public class Main {
    public static void main(String[] args) {
        System.out.println(Main.class.getName());
    }
}

```

package 声明类所属命名空间，getName 返回全限定类名。

```java
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        int[] a = {3, 1, 2};
        Arrays.sort(a);
        System.out.println(Arrays.toString(a));
    }
}

```

import 导入其他包的类，避免使用全限定名，提高代码可读性。

## 概念定义与适用场景

包解决的是类命名空间组织与访问控制的问题。它通过层级路径隔离同名类，package 声明当前命名空间，import 引用外部类。

## 语法、API 与边界

本课使用字符串操作处理类全名输入。输入为全限定类名，输出为包名部分。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要用通配符 import（import java.util.*），应明确导入具体类。包名应全小写。提交前应覆盖单层包、多层包和无包名的处理。
