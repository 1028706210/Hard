---
id: csharp-foundations-operators
title: C# 运算符
concepts: [variables, control-flow]
objectives:
  - 使用算术、比较与逻辑运算符。
  - 理解优先级并用括号表达意图。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-operators.html
source_snapshot_date: 2026-08-23
---

# C# 运算符

## 概念定义与适用场景

运算符组合值并产生新结果，基础课程重点是算术、比较和逻辑表达式。

```csharp
var total = 2 + 3 * 4;
Console.WriteLine(total);
```

## 语法、API 与边界

* 与 / 先于 + 与 -；比较产生 bool，&& 和 || 支持短路求值。

```csharp
var age = 20;
var allowed = age >= 18 && age < 65;
Console.WriteLine(allowed);
```

## 常见错误与实践建议

不要忽略整数除法、除零风险或复杂表达式的优先级；必要时使用括号。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
