---
id: cpp-capstone-new
title: C++ <new>
concepts: [memory]
objectives:
  - 会用 new[]/delete[] 成对管理动态数组。
  - 理解分配失败抛 bad_alloc 与异常安全边界。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-new.html
source_snapshot_date: 2026-08-23
---

# C++ <new>

## 概念定义与适用场景

`<new>` 支持 new 表达式与 bad_alloc 异常。new int[n] 分配数组、delete[] 释放；分配失败默认抛 std::bad_alloc 而非返回空指针。

```cpp
#include <iostream>
#include <new>

int* items = new int[3];
items[0] = 3;
items[1] = 4;
items[2] = 5;
delete[] items;
```

## 语法、API 与边界

new[] 必须配 delete[]（配 delete 是未定义行为）；n 为 0 时 new[] 返回合法但不可解引用的指针。std::nothrow 版本失败返回 nullptr。

```cpp
int* spare = new (std::nothrow) int[8];
if (spare == nullptr) {
    // 处理分配失败
}
delete[] spare;
```

## 常见错误与实践建议

常见错误：忘记 delete[] 泄漏、异常路径跳过释放。生产代码优先 vector/unique_ptr，裸 new 只用于底层实现。本课练习要求用 new[] 求平方和并在结束前 delete[]。
