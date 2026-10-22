---
id: csharp-oop-strings
title: 字符串
concepts: [strings, types]
objectives:
  - 用 Length、索引与相等比较安全地处理文本输入。
  - 区分序数比较、忽略大小写比较与区域敏感比较。
prerequisites: [csharp-oop-arrays]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-string.html
source_snapshot_date: 2026-08-23
---

# 字符串

## 概念定义与适用场景

string 是不可变的引用类型：任何"修改"操作都会返回新的字符串实例。判断用户输入是否匹配、比较口令或标签时，核心是选择正确的比较方式，而不是反复拼接。

```csharp
var text = "CSharp";
Console.WriteLine(text.Length);
Console.WriteLine(text[0]);
```

## 语法、API 与边界

`==` 对 string 执行值比较。需要控制比较规则时使用 `Equals(other, StringComparison)`：`Ordinal` 逐字符比较代码单元，`OrdinalIgnoreCase` 在此基础上忽略大小写。`s[0]` 在 s 为空字符串时抛出 IndexOutOfRangeException，访问前先检查 Length。

```csharp
var first = Console.ReadLine() ?? "";
var second = Console.ReadLine() ?? "";
if (first.Equals(second, StringComparison.OrdinalIgnoreCase))
{
    Console.WriteLine("match");
}
```

## 常见错误与实践建议

`ToUpper`/`ToLower` 不带 Invariant 后缀时遵循当前区域，土耳其语 i 等规则可能产生意外结果，程序化比较应使用 `ToUpperInvariant` 或 `OrdinalIgnoreCase`。字符串不可变意味着循环拼接会产生大量临时对象，本课只演示只读访问与比较。空行与文件末尾读到的 null 都要单独成分支处理。
