---
id: java-foundations-switch
title: Java switch case
concepts: [variables, control-flow]
objectives:
  - 解释case、default 和分支输出在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java switch case。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-switch-case.html
source_snapshot_date: 2026-08-23
---

# Java switch case

## 概念定义与适用场景

switch适合离散映射，default覆盖未列出的值。JDK17箭头分支不发生传统case贯穿；不要遗漏未知值，也不要把输入错误当作default。

## 语法、API 与边界

读取Java int范围整数n，switch将1映射为read、2映射为code、3映射为test，其余整数通过default输出unknown。非整数、超出int范围或空输入无输出，退出码1。支架已解析number。

```java
import java.nio.charset.StandardCharsets;
public class Main {

    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        long n;
        try { n = Long.parseLong(text); } catch (NumberFormatException error) { System.exit(1); return; }
        if (n < Integer.MIN_VALUE || n > Integer.MAX_VALUE) { System.exit(1); return; }
        int number = (int)n;
        String action = switch (number) { case 1 -> "read"; case 2 -> "code"; case 3 -> "test"; default -> "unknown"; };
        System.out.println(action);
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## default明确处理未知值

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
int number = 0;
String action = switch (number) {
    case 1 -> "read";
    default -> "unknown";
};
System.out.println(action); // unknown
```
