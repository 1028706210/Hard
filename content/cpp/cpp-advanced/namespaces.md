---
id: cpp-advanced-namespaces
title: C++ 命名空间
concepts: [namespaces]
objectives:
  - 定义命名空间并用作用域运算符访问成员。
  - 理解 using 声明与命名冲突防护。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-namespaces.html
source_snapshot_date: 2026-08-23
---

# C++ 命名空间

## 概念定义与适用场景

命名空间把名称组织进具名作用域，避免不同模块的同名冲突：calc::transform 与 text::transform 互不干扰。std 就是最常见的命名空间。

```cpp
namespace calc {
int transform(int value) {
    return value * 2 + 1;
}
}

int result = calc::transform(3);  // 7
```

## 语法、API 与边界

:: 作用域运算符显式限定访问；using calc::transform 把单个名字引入当前作用域，using namespace calc 引入全部（谨慎使用，易重新引入冲突）。命名空间可以嵌套与分段定义。

```cpp
using std::string;
string name = "cpp";  // 经 using 声明后可直接使用
```

## 常见错误与实践建议

不要在头文件用 using namespace std（污染所有包含方）；同名冲突时优先显式限定而非改名字。本课练习要求通过命名空间限定完成计算。
