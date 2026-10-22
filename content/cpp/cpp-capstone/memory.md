---
id: cpp-capstone-memory
title: C++ <memory>
concepts: [memory]
objectives:
  - 会用 std::unique_ptr 独占管理堆对象生命周期。
  - 理解 make_unique 与 RAII 自动释放的配合。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-memory.html
source_snapshot_date: 2026-08-23
---

# C++ <memory>

## 概念定义与适用场景

`<memory>` 的 unique_ptr 表达独占所有权：离开作用域自动 delete，无需手写释放。make_unique 一步完成分配与构造，异常安全。

```cpp
#include <iostream>
#include <memory>
#include <vector>

auto data = std::make_unique<std::vector<long long>>();
data->push_back(3);
data->push_back(4);
std::cout << (*data)[0] + (*data)[1] << std::endl;   // 7
```

## 语法、API 与边界

unique_ptr 不可拷贝、只能移动；-> 访问成员、* 解引用。get() 取裸指针不转移所有权，release() 才放弃。数组形态 unique_ptr<T[]> 用下标访问。

```cpp
auto buffer = std::make_unique<std::int64_t[]>(4);
buffer[0] = 9;
```

## 常见错误与实践建议

常见错误：对同一指针同时持有裸指针与 unique_ptr 造成二次释放、用 get() 后手动 delete。本课练习要求把 vector 装进 unique_ptr 并通过它完成求和。
