---
id: cpp-capstone-typeinfo
title: C++ <typeinfo>
concepts: [types]
objectives:
  - 会用 typeid 在运行期比较表达式类型。
  - 理解 typeid 忽略顶层 cv 限定与解引用指针的静态类型规则。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-typeinfo.html
source_snapshot_date: 2026-08-23
---

# C++ <typeinfo>

## 概念定义与适用场景

typeid 返回 type_info 引用，可在运行期比较两个表达式的动态类型是否相同。对指针解引用取 typeid 时得到的是指针的静态指向类型，只有多态基类指针才取动态类型。

```cpp
#include <typeinfo>
#include <iostream>

int value = 0;
double other = 0.0;
if (typeid(value) == typeid(other)) {
    std::cout << "same" << std::endl;
} else {
    std::cout << "diff" << std::endl;
}
```

## 语法、API 与边界

type_info 不可拷贝构造，只能通过 typeid 取引用；name() 返回实现相关的修饰名（MinGW 下 int 通常是 "i"），不要把 name() 字符串当稳定标识。顶层 const 与引用会被忽略。

```cpp
const int fixed = 1;
static_assert(typeid(fixed) == typeid(int));
```

## 常见错误与实践建议

常见错误：依赖 name() 输出做逻辑判断、把 typeid 当编译期工具（它不支持模板分支）。本课练习要求用 typeid 比较两个变量的类型并输出 same/diff。
