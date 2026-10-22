---
id: cpp-stl-containers-stack
title: C++ <stack>
concepts: [data-structures]
objectives:
  - 会用 stack 的 push/pop/top 三件套。
  - 会用栈解决括号配对类问题。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-stack.html
source_snapshot_date: 2026-08-23
---

# C++ <stack>

## 概念定义与适用场景

`std::stack<T>` 是后进先出（LIFO）适配器：push 入栈、pop 弹出（不返回值）、top 看栈顶。只暴露顶端，适合撤销、嵌套匹配、深度优先等场景。

```cpp
#include <iostream>
#include <stack>

std::stack<char> pending;
pending.push('(');
pending.push(')');
char top = pending.top();  // ')'
pending.pop();
```

## 语法、API 与边界

pop() 只删除不返回，取值须先 top() 再 pop()；空栈 top/pop 是未定义行为，操作前用 empty() 检查。默认基于 deque 实现，可用 `std::stack<int, std::vector<int>>` 换底层容器。

```cpp
if (!pending.empty()) {
    pending.pop();
}
```

## 常见错误与实践建议

常见错误：把 pop() 当成取值、循环弹栈不做 empty 检查。配对问题里「右括号来了栈却空」即不匹配，应立即判失败。本课练习要求用栈判断括号串是否合法。
