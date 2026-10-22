---
id: java-foundations-comments
title: Java 注释
concepts: [variables, control-flow]
objectives:
  - 解释行注释、块注释与文档注释在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 注释。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-comments.html
source_snapshot_date: 2026-08-23
---

# Java 注释

## 概念定义与适用场景

行注释说明局部意图，块注释适合多行说明，文档注释用于公开接口。注释应解释单位和约束，不能代替真实输入校验；自动输出测试无法判断说明是否准确。

## 语法、API 与边界

读取两个0到1000000的整数left、right，计算矩形面积并输出long结果。为计算语句添加说明单位或假设的行注释。非法数量、负数、越界或非整数无输出，退出码1。自动判题只检查面积，不评价注释质量。支架已校验参数。

```java
import java.nio.charset.StandardCharsets;
public class Main {

    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        String[] parts = text.split("\s+");
        long left, right;
        try {
            if (parts.length != 2) throw new NumberFormatException();
            left = Long.parseLong(parts[0]); right = Long.parseLong(parts[1]);
        } catch (NumberFormatException error) { System.exit(1); return; }
        if (left < 0 || right < 0 || left > 1000000 || right > 1000000) { System.exit(1); return; }
        // 两边使用相同单位，面积使用对应平方单位。
        long area = left * right;
        System.out.println(area);
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## 注释说明约束而非复述语句

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
// 输入边长使用厘米，结果单位为平方厘米。
long width = 3, height = 4;
System.out.println(width * height); // 12
```
