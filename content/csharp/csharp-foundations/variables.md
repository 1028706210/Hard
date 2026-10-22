---
id: csharp-foundations-variables
title: C# 变量
concepts: [variables, control-flow]
objectives:
  - 声明并初始化有意义的变量。
  - 通过赋值表达状态变化。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-variables.html
source_snapshot_date: 2026-08-23
---

# C# 变量

## 概念定义与适用场景

变量是带名称和类型的可变存储位置，用来表达程序运行中的状态。

```csharp
var score = 10;
score += 5;
Console.WriteLine(score);
```

## 语法、API 与边界

声明时可显式写类型或使用 var；读取变量前必须完成确定赋值。

```csharp
string status = "queued";
status = "done";
Console.WriteLine(status);
```

练习中的交换可以用临时变量，也可以用 `(left, right) = (right, left);`：右侧先取得旧值，再写入左侧。随后执行 `left += 1`。例如初值 3 和 8，交换后是 8 和 3，更新后输出 9 和 3。

## 常见错误与实践建议

不要使用无意义名称、重复保存同一状态或在初始化前读取局部变量。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
