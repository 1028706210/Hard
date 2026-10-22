---
id: java-foundations-loops
title: Java 循环结构
concepts: [variables, control-flow]
objectives:
  - 解释for、while 与确定终止在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 循环结构。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-loop.html
source_snapshot_date: 2026-08-23
---

# Java 循环结构

## 概念定义与适用场景

循环让一段操作重复执行。已知次数时常用 `for`：初始化只执行一次，每轮先判断条件，执行循环体后更新计数。下面累加 1、2、3，输出 6。

```java
public class Main {
    public static void main(String[] args) {
        int sum = 0;
        for (int i = 1; i <= 3; i++) {
            sum += i;
        }
        System.out.println(sum);
    }
}
```

## 语法、API 与边界

`while` 也先判断条件，适合根据状态决定是否继续。下面输出 3、2、1，每次减 1 使条件最终变为 false。如果初始值是 0，循环体一次也不执行。

```java
public class Main {
    public static void main(String[] args) {
        int remaining = 3;
        while (remaining > 0) {
            System.out.println(remaining);
            remaining--;
        }
    }
}
```

练习从标准输入读取 0 到 1000 的一个整数 n，累加 1 到 n。用 `Scanner.hasNextInt()` 检查整数，用 `nextInt()` 取值；再检查范围及是否还有多余输入。非法输入调用 `System.exit(1)`，合法输入只输出和。

## 常见错误与实践建议

`i < n` 与 `i <= n` 相差最后一项；初始化 `sum = 0` 才能正确处理 n 为 0。不要把 `for (...)` 后面的分号写成空循环体，也不要忘记更新 `while` 的控制变量。先手工跟踪 n 为 0、1、4 的结果，再运行程序验证。
