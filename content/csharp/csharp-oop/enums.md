---
id: csharp-oop-enums
title: 枚举
concepts: [enums, types]
objectives:
  - 定义带显式底层值的枚举并在枚举与整数、字符串之间转换。
  - 解释未定义枚举值不抛异常的边界行为与安全解析方式。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-enum.html
source_snapshot_date: 2026-08-23
---

# 枚举

## 概念定义与适用场景

enum 把一组相关的命名常量组织成一个新类型。状态机、级别、方向这类取值有限且固定的概念，用枚举能防止调用方传入任意魔法数字。

```csharp
enum Level
{
    Low = 1,
    Medium = 2,
    High = 3
}
```

## 语法、API 与边界

不显式赋值时第一个成员默认为 0，后续成员依次加一。`(Level)99` 这样的强制转换不会抛异常，得到的是一个未定义的枚举值，因此外部输入要先校验再转换。字符串到枚举用 `Enum.TryParse`，它默认区分大小写，且对数字字符串也可能成功，解析结果应再与原文本核对。

```csharp
var text = Console.ReadLine() ?? "";
if (Enum.TryParse(text, out Level parsed) && text == parsed.ToString())
{
    Console.WriteLine((int)parsed);
}
```

## 常见错误与实践建议

把 `(int)level` 与 `level.ToString()` 的方向写反是常见笔误：前者转成底层整数，后者转回名称。校验外部输入时不要只依赖 TryParse 成功，还要排除未定义的数字值。本课练习同时覆盖"数字转名称"和"名称转数字"两个方向，并要求对越界值按失败处理。
