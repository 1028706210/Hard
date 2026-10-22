---
id: cpp-capstone-type-traits
title: C++ <type_traits>
concepts: [types, generics]
objectives:
  - 会用 is_integral_v/is_floating_point_v 等编译期谓词分支。
  - 理解类型特征在编译期求值、不产生运行开销。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-type_traits.html
source_snapshot_date: 2026-08-23
---

# C++ <type_traits>

## 概念定义与适用场景

类型特征在编译期回答「这个类型是什么」：is_integral_v<T>、is_floating_point_v<T> 是 bool 常量，配合 if constexpr 让同一模板按类型走不同分支，且不成立的分支不参与实例化。

```cpp
#include <type_traits>
#include <iostream>

static_assert(std::is_integral_v<int>, "int 是整型");

template <typename T>
const char* category() {
    if constexpr (std::is_integral_v<T>) return "integral";
    else if constexpr (std::is_floating_point_v<T>) return "floating";
    else return "other";
}
```

## 语法、API 与边界

常用谓词成对出现：is_integral/is_floating_point/is_same/is_pointer/is_reference；带 _v 后缀的是 C++17 起的值版本。if constexpr 的条件必须是编译期常量，else 分支里不合法的代码会被丢弃而不报错。

```cpp
static_assert(std::is_same_v<int, int32_t> || std::is_same_v<int, int64_t>);
static_assert(!std::is_pointer_v<int>);
```

## 常见错误与实践建议

常见错误：把类型特征当运行函数调用、对非 const 求值写 static_assert 却依赖实现细节（如假设 int 恰为 4 字节以外的尺寸）。本课练习要求按类型名输出尺寸与类别，类别判定必须走 if constexpr 谓词分支。
