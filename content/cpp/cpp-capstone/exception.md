---
id: cpp-capstone-exception
title: C++ <exception>
concepts: [exceptions]
objectives:
  - 会用 std::exception 基类按引用捕获并读取 what()。
  - 理解基类 catch 能接住所有标准库异常。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-exception.html
source_snapshot_date: 2026-08-23
---

# C++ <exception>

## 概念定义与适用场景

`<exception>` 定义异常体系根类 std::exception。按 const 引用捕获基类即可统一处理 runtime_error、logic_error 等派生异常，并通过 what() 读取失败描述。

```cpp
#include <exception>
#include <iostream>
#include <stdexcept>

int value = -3;
try {
    if (value < 0) throw std::runtime_error("negative");
    std::cout << value * 2 << std::endl;
} catch (const std::exception& error) {
    std::cout << "error" << std::endl;
}
```

## 语法、API 与边界

catch 必须按 const 引用接收，按值捕获会切掉派生部分；基类 catch 放在派生 catch 之后否则派生分支永远不可达。throw; 可在 catch 内重新抛出原异常。

```cpp
try {
    throw std::runtime_error("demo");
} catch (const std::exception&) {
    throw;   // 原样向上传播
}
```

## 常见错误与实践建议

常见错误：空 catch 吞掉异常、按值捕获导致对象切片。本课练习要求负数输入走抛出-捕获路径输出 error，非负走正常路径。
