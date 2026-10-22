---
id: cpp-algorithms-concurrency-functional
title: C++ <functional>
concepts: [functions]
objectives:
  - 会用 std::function 保存可调用对象。
  - 会把 lambda 传给 count_if 等算法做谓词计数。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-functional.html
source_snapshot_date: 2026-08-23
---

# C++ <functional>

## 概念定义与适用场景

`<functional>` 提供可调用对象的通用工具：std::function<T> 能装下 lambda、函数指针等任何签名匹配的可调用体；std::bind 与占位符可部分绑定参数。算法的谓词参数是它们最常见的舞台。

```cpp
#include <algorithm>
#include <functional>
#include <vector>

std::function<bool(int)> is_even = [](int value) {
    return value % 2 == 0;
};
std::vector<int> values = {1, 2, 3, 4};
int evens = static_cast<int>(std::count_if(values.begin(), values.end(), is_even));
```

## 语法、API 与边界

count_if 统计谓词为 true 的元素个数；lambda 捕获列表 [&] 按引用捕获、[=] 按值捕获，悬垂引用是常见坑。std::function 有一次堆分配的可能，热路径可用模板参数代替。

```cpp
int threshold = 10;
auto above = [threshold](int value) { return value > threshold; };
```

## 常见错误与实践建议

常见错误：lambda 捕获局部变量后异步调用（悬垂）、谓词带副作用破坏计数语义。谓词应保持纯函数。本课练习要求用谓词统计偶数个数。
