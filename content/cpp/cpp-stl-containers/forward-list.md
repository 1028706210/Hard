---
id: cpp-stl-containers-forward-list
title: C++ <forward_list>
concepts: [collections]
objectives:
  - 会用 forward_list 的 push_front 与单向遍历。
  - 理解单向链表比双向链表更省内存的取舍。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-forward_list.html
source_snapshot_date: 2026-08-23
---

# C++ <forward_list>

## 概念定义与适用场景

`std::forward_list<T>` 是单向链表：每个节点只存一个后继指针，比 list 省一个指针的内存，但只能从头向前走，没有 back()/size()。适合只需顺序扫描、频繁头插的场景。

```cpp
#include <forward_list>
#include <iostream>

std::forward_list<std::string> words;
words.push_front("alpha");
words.push_front("beta");   // 现在头部是 beta
```

## 语法、API 与边界

push_front 后新元素即成为头部，front() 取头；没有 size()（为了不存计数），需要个数就自己数。反向遍历不可行——没有 rbegin/rend。

```cpp
std::string head = words.front();      // "beta"
for (const std::string& word : words) {
    std::cout << word << " ";          // beta alpha
}
```

## 常见错误与实践建议

常见错误：调用不存在的 size()/back()、需要逆序处理却选了单向链表。只要用到尾部操作就该选 list 或 deque。本课练习要求 push_front 读取单词后输出头部。
