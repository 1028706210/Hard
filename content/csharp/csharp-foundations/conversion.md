---
id: csharp-foundations-conversion
title: C# 类型转换
concepts: [variables, control-flow]
objectives:
  - 区分隐式转换与显式转换。
  - 用 TryParse 处理不可信文本输入。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-type-conversion.html
source_snapshot_date: 2026-08-23
---

# C# 类型转换

## 概念定义与适用场景

类型转换把值从一种表示变为另一种表示，必须明确精度损失和失败路径。

```csharp
int units = 4;
double exact = units;
Console.WriteLine(exact);
```

## 语法、API 与边界

扩大数值范围通常可隐式转换；缩小转换要显式 cast，文本输入优先使用 TryParse。

```csharp
var ok = int.TryParse("42", out var value);
Console.WriteLine(ok ? value : -1);
```

## 常见错误与实践建议

不要用 Parse 处理未经校验的输入，也不要忽略小数转整数时的截断。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
