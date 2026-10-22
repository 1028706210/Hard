---
id: cpp-capstone-cwchar
title: C++ <cwchar>
concepts: [strings]
objectives:
  - 会用 mbstowcs 与 wcscmp 完成宽字符串转换与比较。
  - 理解宽字符串比较按码点字典序进行。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-cwchar.html
source_snapshot_date: 2026-08-23
---

# C++ <cwchar>

## 概念定义与适用场景

`<cwchar>` 是宽字符版 C 库：mbstowcs 把多字节串转 wchar_t 数组，wcscmp 按码点比较宽字符串。宽字符路径适合需要逐码点处理的文本逻辑。

```cpp
#include <cwchar>
#include <iostream>

wchar_t buffer[16];
std::mbstowcs(buffer, "apple", 16);
std::wcout << (std::wcscmp(buffer, L"apple") == 0) << std::endl;   // 1
```

## 语法、API 与边界

mbstowcs 返回转换的宽字符数（含失败时 -1 转成 size_t 的值）；目标缓冲区必须足够大。wcscmp 返回 <0/0/>0 三态，不能只当布尔用。

```cpp
wchar_t other[16];
std::mbstowcs(other, "banana", 16);
if (std::wcscmp(buffer, other) < 0) {
    // apple 排在 banana 前
}
```

## 常见错误与实践建议

常见错误：缓冲区太小导致截断、宽窄格式混用 printf/wprintf。本课练习要求把两个单词转宽字符串后按 wcscmp 输出字典序较小者。
