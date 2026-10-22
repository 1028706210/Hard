---
id: csharp-oop-arrays
title: 数组
concepts: [arrays, collections]
objectives:
  - 用 Length 属性和合法索引遍历一维数组。
  - 解释数组长度固定、越界访问抛异常的边界行为。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-array.html
source_snapshot_date: 2026-08-23
---

# 数组

## 概念定义与适用场景

数组是一段长度固定、元素类型相同的连续存储。元素个数在创建时就确定、之后按位置访问的场景适合用数组，例如固定窗口的一批读数或按序处理的缓冲。

```csharp
var readings = new int[3];
readings[0] = 8;
readings[1] = 15;
readings[2] = 4;
Console.WriteLine(readings.Length);
```

## 语法、API 与边界

`new int[5]` 创建的每个元素默认初始化为 0；`arr[arr.Length - 1]` 是最后一个元素，访问 `arr[arr.Length]` 会抛出 IndexOutOfRangeException。从后向前遍历用 `for (var i = arr.Length - 1; i >= 0; i--)`。

```csharp
var words = Console.ReadLine()?.Split(' ', StringSplitOptions.RemoveEmptyEntries) ?? [];
for (var i = words.Length - 1; i >= 0; i--)
{
    Console.WriteLine(words[i]);
}
```

## 常见错误与实践建议

数组长度创建后不能增减，需要更多空间时只能创建新数组并复制。循环边界最常见的错误是把 `<` 写成 `<=`，导致刚好越界一个元素。空输入要先判元素个数再决定输出，而不是访问第一个元素。本课练习只使用一维数组和标准输入输出。
