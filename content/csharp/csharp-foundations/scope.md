---
id: csharp-foundations-scope
title: C# 变量作用域
concepts: [variables, control-flow]
objectives:
  - 判断局部变量的可见范围。
  - 用代码块限制临时状态的生命周期。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-variable-scope.html
source_snapshot_date: 2026-08-23
---

# C# 变量作用域

## 概念定义与适用场景

作用域决定名称在何处可见，较小作用域能减少状态之间的意外干扰。

```csharp
var total = 0;
{ var item = 3; total += item; }
Console.WriteLine(total);
```

## 语法、API 与边界

方法体和花括号代码块都会建立局部范围；内层代码可以读取外层已声明变量。

```csharp
if (true) { var message = "inside"; Console.WriteLine(message); }
```

## 常见错误与实践建议

不要在块外引用内部变量，也不要用同名变量遮蔽重要状态。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
