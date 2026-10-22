---
id: csharp-foundations-loops
title: C# 循环
concepts: [variables, control-flow]
objectives:
  - 选择 for、while 完成有限重复。
  - 设置终止条件避免无限循环。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-loops.html
source_snapshot_date: 2026-08-23
---

# C# 循环

## 概念定义与适用场景

循环在终止条件成立前重复执行代码，适合计数、累计和逐项处理。

```csharp
var sum = 0;
for (var i = 1; i <= 3; i++) sum += i;
Console.WriteLine(sum);
```

## 语法、API 与边界

for 适合已知次数，while 适合由状态决定次数；循环变量应朝终止条件推进。

```csharp
var remaining = 2;
while (remaining > 0) { Console.WriteLine(remaining); remaining--; }
```

## 常见错误与实践建议

不要遗漏更新语句、修改错误变量或制造无法终止的条件。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
