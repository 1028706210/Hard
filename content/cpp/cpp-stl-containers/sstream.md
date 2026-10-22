---
id: cpp-stl-containers-sstream
title: C++ <sstream>
concepts: [strings]
objectives:
  - 会用 istringstream 按流式方式拆分字符串。
  - 会用 ostringstream 拼接格式化文本。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-sstream.html
source_snapshot_date: 2026-08-23
---

# C++ <sstream>

## 概念定义与适用场景

`<sstream>` 把字符串变成流：istringstream 从文本中按 `>>` 拆词或解析数字，ostringstream 把各类型拼成一个字符串。它是「字符串 ↔ 数值」转换与文本拆分的标准做法，比手工截取更安全。

```cpp
#include <sstream>
#include <string>

std::string text = "10 20 30";
std::istringstream reader(text);
int value = 0;
int total = 0;
while (reader >> value) {
    total += value;
}
```

## 语法、API 与边界

istringstream 读完会进入 eof/fail 状态，可以用 `while (reader >> value)` 自然终止；流只读一次，要重读需 clear 后重新 seek 或重建。ostringstream 用 .str() 取出结果。

```cpp
std::ostringstream writer;
writer << "total=" << total;
std::string result = writer.str();
```

## 常见错误与实践建议

常见错误：拆词循环里不检查流状态、把同一个 istringstream 重复使用而不重置。建议每次解析新建流或用 str(text) 重置内容。本课练习要求用 istringstream 拆一行整数求和。
