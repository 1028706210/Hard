---
id: csharp-foundations-constants
title: C# 常量
concepts: [variables, control-flow]
objectives:
  - 区分 const、只读意图与普通变量。
  - 用命名常量消除含义不明的字面量。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-constants.html
source_snapshot_date: 2026-08-23
---

# C# 常量

## 概念定义与适用场景

常量表示编译期不应变化的值，命名能让规则含义比裸字面量更清楚。

```csharp
const int DaysPerWeek = 7;
Console.WriteLine(DaysPerWeek * 2);
```

## 语法、API 与边界

const 适用于编译期常量，名称通常采用清晰的 PascalCase；运行期只读状态留给后续对象课程。

```csharp
const decimal TaxRate = 0.05m;
Console.WriteLine(100m * TaxRate);
```

## 常见错误与实践建议

不要把会随输入变化的值声明为 const，也不要散落重复的魔法数字。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
