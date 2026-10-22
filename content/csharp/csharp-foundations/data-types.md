---
id: csharp-foundations-data-types
title: C# 数据类型
concepts: [variables, control-flow]
objectives:
  - 区分整数、浮点数、布尔值和字符串。
  - 根据数据含义选择合适类型。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-data-types.html
source_snapshot_date: 2026-08-23
---

# C# 数据类型

## 概念定义与适用场景

数据类型限定值的表示范围和可用操作，选择类型应依据业务含义而不是只看样例。

```csharp
int count = 3;
double price = 2.5;
Console.WriteLine(count * price);
```

## 语法、API 与边界

int、double、bool 和 string 覆盖常见基础数据；var 仍由编译器推断出静态类型。

```csharp
bool available = true;
string label = available ? "yes" : "no";
Console.WriteLine(label);
```

## 常见错误与实践建议

不要用整数除法期待小数，也不要把可能溢出的值塞入过小类型。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
