---
id: csharp-foundations-basic-syntax
title: C# 基本语法
concepts: [variables, control-flow]
objectives:
  - 正确书写语句、标识符和注释。
  - 从编译错误定位基础语法问题。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-basic-syntax.html
source_snapshot_date: 2026-08-23
---

# C# 基本语法

## 概念定义与适用场景

基本语法规定标识符、字面量、注释和语句的书写方式，是编译器理解程序的基础。

```csharp
var message = "syntax ok";
Console.WriteLine(message);
```

## 语法、API 与边界

标识符区分大小写；双引号表示字符串，单引号表示字符，// 与 /* */ 用于注释。

```csharp
char grade = 'A'; // 单个字符
Console.WriteLine(grade);
```

## 常见错误与实践建议

不要遗漏分号、混淆大小写或使用未声明名称；先读第一条编译诊断。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
