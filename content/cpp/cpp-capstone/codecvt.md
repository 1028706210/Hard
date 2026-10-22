---
id: cpp-capstone-codecvt
title: C++ <codecvt>
concepts: [strings, io]
objectives:
  - 会完成窄字符串与 wstring 的转换并处理宽字符。
  - 理解 codecvt 系列 C++17 起弃用的边界。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-codecvt.html
source_snapshot_date: 2026-08-23
---

# C++ <codecvt>

## 概念定义与适用场景

`<codecvt>` 提供字符编码转换 facet（codecvt_utf8 等），C++17 起标记弃用但概念仍在：窄字符（char）与宽字符（wchar_t）之间的转换必须显式发生，且转换是逐码点的映射。

```cpp
#include <iostream>
#include <string>

std::string narrow = "hard";
std::wstring wide(narrow.begin(), narrow.end());   // ASCII 直映射
std::wcout << wide.size() << std::endl;             // 4
```

## 语法、API 与边界

ASCII 区间 char↔wchar_t 一一对应；非 ASCII 用 mbstowcs 或平台 API。弃用的 codecvt_utf8 仍可用但新代码应避免。宽字符的算术运算按码点值进行。

```cpp
wchar_t letter = L'a';
int position = static_cast<int>(letter - L'a') + 1;   // 1
```

## 常见错误与实践建议

常见错误：窄宽混用输出乱码、以为 string 字节数等于字符数（UTF-8 下不等）。本课练习要求转 wstring 后按码点求字母值之和（a=1..z=26）。
