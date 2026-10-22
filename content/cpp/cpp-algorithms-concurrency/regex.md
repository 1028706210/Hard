---
id: cpp-algorithms-concurrency-regex
title: C++ <regex>
concepts: [regular-expressions]
objectives:
  - 会构造 std::regex 并用 regex_match 全串匹配。
  - 会用字符类与量词表达格式合同。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-regex.html
source_snapshot_date: 2026-08-23
---

# C++ <regex>

## 概念定义与适用场景

`<regex>` 提供正则表达式：std::regex 编译模式，regex_match 判断整个字符串是否匹配，regex_search 在串中查找。适合格式校验（编号、电话、邮箱形状）。

```cpp
#include <iostream>
#include <regex>
#include <string>

std::regex pattern("CPP-[0-9]{1,3}");
std::string code = "CPP-42";
bool valid = std::regex_match(code, pattern);   // true
```

## 语法、API 与边界

regex_match 要求整串匹配（等价 ^...$），regex_search 只要找到子串；量词 {1,3} 表示 1 到 3 位，[0-9] 是数字字符类。非法模式在构造 regex 时抛 regex_error。

```cpp
std::regex shaped("[A-Z]+[0-9]*");
bool ok = std::regex_match("AB12", shaped);   // true
```

## 常见错误与实践建议

常见错误：以为 regex_match 是部分匹配、每次循环重复构造同一个 regex（应构造一次复用）。格式合同写成模式后用边界值测两端。本课练习要求校验编号格式。
