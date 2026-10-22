---
id: cpp-capstone-useful-resources
title: C++ 有用的资源
concepts: [tooling]
objectives:
  - 会按用途给学习资源分类并统计。
  - 理解资源清单的可验证性与本地化整理。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-useful-resources.html
source_snapshot_date: 2026-08-23
---

# C++ 有用的资源

## 概念定义与适用场景

资源页的价值不在链接列表，而在「用途标注」：官方文档查标准合同、参考站查 API 形态、编译器文档查实现边界。把资源按用途归类后，检索路径可复现。

```cpp
#include <iostream>
#include <string>

std::string name = "cppreference";
std::string purpose = "标准合同";
std::cout << name << ": " << purpose << std::endl;
```

## 语法、API 与边界

整理清单时每条记录至少三元组：名称、类别、用途。类别用受限词表（如 docs/tutorial/forum）避免自由文本发散，统计才可靠。

```cpp
// 受限词表：cpp / python / other
```

## 常见错误与实践建议

常见错误：收藏链接却无用途标注、把过期教程当现行标准。本课练习要求读入资源条目并按受限类别统计数量，未知类别整体拒绝。
