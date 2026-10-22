---
id: cpp-stl-containers-iostream
title: C++ <iostream>
concepts: [io]
objectives:
  - 掌握 cin 逐词读取与 getline 整行读取的区别。
  - 会处理流失败状态并转为非零退出。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-iostream.html
source_snapshot_date: 2026-08-23
---

# C++ <iostream>

## 概念定义与适用场景

`<iostream>` 提供四个标准流对象：cin（输入）、cout（输出）、cerr（错误）、clog（日志）。`>>` 按空白切词读取，getline(cin, s) 读取整行保留空格，两者混用时注意 `>>` 会把换行留在流里。

```cpp
#include <iostream>
#include <string>

std::string word;
std::cin >> word;                 // 读一个词
std::string line;
std::getline(std::cin, line);     // 读一整行
```

## 语法、API 与边界

读取失败（输入耗尽或类型不符）会置流为 fail 状态，后续读取全部失效；应立即检查并退出。cerr 不缓冲，适合错误信息；cout 可被重定向。

```cpp
int count = 0;
if (!(std::cin >> count)) {
    return 1;  // 输入不合法直接失败
}
```

## 常见错误与实践建议

常见错误：`>>` 后直接 getline 读到空行残留、不检查流状态继续算出垃圾值。建议边界输入先验证再使用。本课练习要求用 getline 统计行长。
