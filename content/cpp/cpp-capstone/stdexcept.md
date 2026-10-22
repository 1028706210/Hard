---
id: cpp-capstone-stdexcept
title: C++ <stdexcept>
concepts: [exceptions]
objectives:
  - 会用 out_of_range/range_error 等标准异常表达越界失败。
  - 理解 at() 与 operator[] 的异常差异。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-stdexcept.html
source_snapshot_date: 2026-08-23
---

# C++ <stdexcept>

## 概念定义与适用场景

`<stdexcept>` 提供带消息的标准异常族：out_of_range、invalid_argument、overflow_error 等。vector::at() 越界抛 out_of_range，是「可恢复失败」的标准表达方式。

```cpp
#include <iostream>
#include <stdexcept>
#include <vector>

std::vector<int> values{10, 20, 30};
try {
    std::cout << values.at(1) << std::endl;   // 20
} catch (const std::out_of_range&) {
    std::cout << "out_of_range" << std::endl;
}
```

## 语法、API 与边界

at() 做边界检查并抛异常；operator[] 不检查，越界是未定义行为。构造异常时传入字符串消息，what() 原样返回。捕获派生异常前不要先捕获基类。

```cpp
if (index < 0) throw std::invalid_argument("index");
```

## 常见错误与实践建议

常见错误：用 operator[] 自行检查越界（条件写错就是 UB）、用异常做正常控制流。本课练习要求用 at()/out_of_range 处理下标访问，越界输出 out_of_range。
