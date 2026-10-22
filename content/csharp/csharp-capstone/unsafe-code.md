---
id: csharp-capstone-unsafe-code
title: 不安全代码与指针边界
concepts: [memory, types]
objectives:
  - 理解 unsafe、指针、取址与解引用的适用边界，并区分托管引用和原始内存地址。
  - 在服务端专用模板中使用 fixed 固定数组并安全遍历元素，同时保持普通练习默认禁用不安全代码。
prerequisites: [csharp-language-features-generics]
difficulty: advanced
experience_points: 40
source_url: https://www.runoob.com/csharp/csharp-unsafe-codes.html
source_snapshot_date: 2026-08-23
---

# 不安全代码与指针边界

## 概念定义与适用场景

C# 默认通过托管引用访问对象，运行时可以跟踪对象并在垃圾回收时移动它们。`unsafe` 代码允许直接声明和解引用指针，适用于与原生接口互操作、处理固定布局缓冲区或经过测量后确有必要的底层路径。它不是“运行更快”的通用开关，也不会绕过输入校验、数组边界设计和资源所有权规则。

```csharp
unsafe
{
    var value = 12;
    int* address = &value;
    Console.WriteLine(*address);
}
```

## 语法、API 与边界

`&value` 取得地址，`*pointer` 解引用，`pointer + 1` 按目标类型大小前进。托管数组可能被垃圾回收器移动，所以只能在 `fixed` 语句的有限作用域内取得稳定地址。指针不能指向已经离开生命周期的局部数据，也不能在不知道长度时向前遍历。

```csharp
var values = new[] { 3, 5, 8 };
unsafe
{
    fixed (int* start = values)
    {
        long sum = 0;
        for (var index = 0; index < values.Length; index++)
            sum += *(start + index);
        Console.WriteLine(sum);
    }
}
```

本平台只有本课的专用练习由服务端内部白名单启用 `AllowUnsafeBlocks`。课程 JSON、浏览器请求、用户源码和前端都不能设置该能力；其他 C# 练习继续使用默认的安全模板。

## 常见错误与实践建议

常见错误包括把 `unsafe` 当成免校验通道、在 `fixed` 作用域外保存指针、把元素数量和字节数量混用，以及让用户控制编译参数。优先使用 `Span<T>`、数组和安全的库 API；只有边界清晰、生命周期可证明且普通 API 不能满足要求时才使用指针。本课练习先完整校验整数数量和范围，再进入很小的 `fixed` 作用域求和。
