---
id: java-capstone-examples
title: Java 实例
concepts: [control-flow, collections]
objectives:
  - 掌握Java 实例的核心概念与使用方式。
  - 用正常、边界和失败输入验证Java 实例。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-examples.html
source_snapshot_date: 2026-08-23
---

# Java 实例

Java 实例通过完整的可运行程序展示语言特性。每个实例聚焦一个主题，结合输入处理、逻辑运算和输出格式化。

```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        int[] nums = {1, 2, 3, 4, 5, 6};
        int even = 0;
        for (int n : nums) if (n % 2 == 0) even++;
        System.out.println(even);
    }
}
```

遍历数组并用取模运算统计偶数个数，是基础的实例编程模式。

```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        String line = "add 3 5";
        String[] p = line.split(" ");
        int a = Integer.parseInt(p[1]), b = Integer.parseInt(p[2]);
        System.out.println(p[0].equals("add") ? a + b : a - b);
    }
}
```

解析命令行式输入并执行运算，是实例编程中常见的解析-执行模式。

## 概念定义与适用场景

Java 实例解决的是通过完整可运行程序验证语言特性掌握程度的问题。每个实例聚焦输入解析、逻辑运算和格式化输出的完整链路。

## 语法、API 与边界

本课使用数组遍历和条件判断处理整数序列输入。输入为逗号分隔整数，输出为偶数数量。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要忽略边界情况（空输入、单元素、全奇/全偶）。实例程序应让每次运行自行结束。提交前应覆盖正常、边界和失败输入的完整验证。
