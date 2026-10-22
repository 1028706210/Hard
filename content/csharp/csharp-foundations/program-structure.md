---
id: csharp-foundations-program-structure
title: C# 程序结构
concepts: [variables, control-flow]
objectives:
  - 识别语句、代码块和程序入口。
  - 组织可独立结束的控制台程序。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-program-structure.html
source_snapshot_date: 2026-08-23
---

# C# 程序结构

## 概念定义与适用场景

程序结构描述入口、语句和代码块的层级，让执行顺序与变量生命周期可见。

```csharp
var started = true;
if (started) { Console.WriteLine("start"); }
```

## 语法、API 与边界

顶级语句适合小练习；花括号形成代码块，分号结束大多数语句。

```csharp
for (var step = 1; step <= 2; step++) { Console.WriteLine(step); }
```

## 常见错误与实践建议

不要混用多个入口，也不要在代码块外引用局部变量。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
