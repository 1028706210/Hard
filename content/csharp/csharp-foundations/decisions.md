---
id: csharp-foundations-decisions
title: C# 判断
concepts: [variables, control-flow]
objectives:
  - 使用 if、else if 和 else 描述互斥规则。
  - 保证每个输入都进入明确分支。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-decision.html
source_snapshot_date: 2026-08-23
---

# C# 判断

## 概念定义与适用场景

判断根据布尔条件选择互斥路径，使不同输入得到明确结果。

```csharp
var score = 82;
if (score >= 60) Console.WriteLine("pass"); else Console.WriteLine("retry");
```

## 语法、API 与边界

if 处理首个条件，else if 继续分类，else 覆盖剩余情况；条件必须是 bool。

```csharp
var value = 0;
Console.WriteLine(value > 0 ? "positive" : value < 0 ? "negative" : "zero");
```

## 常见错误与实践建议

不要遗漏边界值、写永远无法到达的分支或让多个互斥规则重叠。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
