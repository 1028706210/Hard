---
id: csharp-foundations-introduction
title: C# 简介
concepts: [variables, control-flow]
objectives:
  - 说明 C#、.NET 与控制台程序的关系。
  - 识别编译与执行阶段的职责。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-intro.html
source_snapshot_date: 2026-08-23
---

# C# 简介

## 概念定义与适用场景

C# 是运行在 .NET 上的静态类型语言，适合构建从小型工具到服务端应用的多种程序。

```csharp
var language = "C#";
Console.WriteLine($"{language} on .NET");
```

## 语法、API 与边界

源文件由 SDK 编译为程序集，再由 .NET 运行时执行；语言版本和运行时版本不是同一概念。

```csharp
Console.WriteLine(Environment.Version.Major > 0 ? "runtime-ready" : "runtime-missing");
```

## 常见错误与实践建议

不要把 C# 与某个 IDE 绑定，也不要假定任意 .NET 包都已离线可用。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
