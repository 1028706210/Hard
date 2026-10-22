---
id: cpp-core-memory-data-structures
title: C++ 数据结构
concepts: [data-structures]
objectives:
  - 用 vector 组合实现栈等基础数据结构。
  - 按访问模式选择容器并维护结构不变量。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-data-structures.html
source_snapshot_date: 2026-08-23
---

# C++ 数据结构

## 概念定义与适用场景

数据结构按访问模式组织数据：栈（后进先出）适合撤销与匹配，队列（先进先出）适合排队处理，链表适合频繁中间插删。C++ 中可用 vector 复合实现这些结构，标准库另提供现成容器。

```cpp
#include <vector>

std::vector<int> stack;
stack.push_back(1);   // 入栈
stack.push_back(2);
stack.pop_back();     // 出栈，剩 [1]
```

## 语法、API 与边界

自实现结构要维护不变量：栈只允许在尾部进出，空栈弹出是缺陷操作。结构选择看操作频率：随机访问选 vector，头尾频繁进出选 deque。

```cpp
if (!stack.empty()) {
    int top = stack.back();  // 取栈顶前先确认非空
    stack.pop_back();
}
```

## 常见错误与实践建议

不要对空容器调用 back()/pop_back()（未定义行为）；操作序列来自外部输入时先校验合法性。本课练习按指令序列维护栈并输出最终内容，模块挑战也挂在本课。
