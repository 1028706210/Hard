---
id: cpp-stl-containers-list
title: C++ <list>
concepts: [collections]
objectives:
  - 会用 std::list 的 push_back 与成员 sort。
  - 理解链表在任意位置插入上的优势与随机访问的代价。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-list.html
source_snapshot_date: 2026-08-23
---

# C++ <list>

## 概念定义与适用场景

`std::list<T>` 是双向链表：节点分散存储，插入/删除只改指针不搬移元素，但随机访问必须从头走。它提供成员版 sort()（对链表特别优化）与 splice（拼接）。

```cpp
#include <iostream>
#include <list>

std::list<int> values;
values.push_back(3);
values.push_back(1);
values.push_back(2);
values.sort();  // 链表自带排序
```

## 语法、API 与边界

成员 sort() 是稳定排序，默认升序；不能对 list 使用 std::sort（需要随机访问迭代器）。插入/删除不会让其他迭代器失效，这是与 vector 的关键差异。

```cpp
for (int value : values) {
    std::cout << value << " ";  // 1 2 3
}
```

## 常见错误与实践建议

常见错误：对 list 调用 std::sort 直接编译失败、用 advance 做频繁随机访问。需要频繁按下标访问就换 vector。本课练习要求 push_back 后用成员 sort 输出升序。
