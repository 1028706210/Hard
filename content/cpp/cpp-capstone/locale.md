---
id: cpp-capstone-locale
title: C++ <locale>
concepts: [strings]
objectives:
  - 会用 locale 感知的 isalpha/isdigit 分类字符。
  - 理解 "C" 经典 locale 与本地化的边界。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-locale.html
source_snapshot_date: 2026-08-23
---

# C++ <locale>

## 概念定义与适用场景

`<locale>` 把文化差异（字母表、排序、数字格式）从代码剥离。传 locale 参数的 isalpha/isdigit 按指定 locale 分类；std::locale::classic() 即 "C" locale，ASCII 范围行为最稳定。

```cpp
#include <cctype>
#include <iostream>
#include <locale>

std::locale classic = std::locale::classic();
char letter = 'a';
if (std::isalpha(letter, classic)) {
    std::cout << "alpha" << std::endl;
}
```

## 语法、API 与边界

locale 对象不可变、可拷贝；name() 返回实现相关名称（classic 恒为 "C"）。分类函数返回 int，非零为真。宽字符用 iswalpha 配 wlocale。

```cpp
int digits = std::isdigit('7', classic) ? 1 : 0;
```

## 常见错误与实践建议

常见错误：直接用 <cctype> 的 isalpha 却期待本地化行为、把 locale 名当跨平台常量。本课练习要求按 classic locale 统计一行字符的字母/数字/其他数量。
