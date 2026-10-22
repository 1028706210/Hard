---
id: cpp-algorithms-concurrency-iterator
title: C++ <iterator>
concepts: [collections]
objectives:
  - 会用 std::find 定位元素并把迭代器换算为下标。
  - 会用 begin/end 与迭代器区间表达位置关系。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-iterator.html
source_snapshot_date: 2026-08-23
---

# C++ <iterator>

## 概念定义与适用场景

迭代器是容器与算法之间的通用游标：begin() 指向首元素、end() 指向尾后。std::find 在区间内查找值，返回首个匹配的迭代器；找不到返回 end。

```cpp
#include <algorithm>
#include <iterator>
#include <vector>

std::vector<int> values = {10, 20, 30};
auto position = std::find(values.begin(), values.end(), 20);
int index = static_cast<int>(position - values.begin());  // 1
```

## 语法、API 与边界

迭代器相减得到元素距离（随机访问迭代器），end 减 begin 即 size；解引用 end 是未定义行为。advance/next/prev 可以移动迭代器，越界移动同样是未定义行为。

```cpp
if (position != values.end()) {
    std::cout << index << std::endl;   // 找到才输出下标
}
```

## 常见错误与实践建议

常见错误：不判 end 就解引用、把 end() 当最后一个元素。查找结果先与 end 比较，再换算下标使用。本课练习要求输出首次出现下标或 -1。
