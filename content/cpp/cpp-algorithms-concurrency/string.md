---
id: cpp-algorithms-concurrency-string
title: C++ <string>
concepts: [strings]
objectives:
  - 会遍历 std::string 统计字符出现次数。
  - 会用 size/substr/at 等成员安全操作文本。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-string.html
source_snapshot_date: 2026-08-23
---

# C++ <string>

## 概念定义与适用场景

`std::string` 是可变长字符序列：getline 读整行，`>>` 读单词；size() 长度、substr 截取、find 查找。逐字符处理用范围 for 最直接。

```cpp
#include <iostream>
#include <string>

std::string text = "banana";
int count = 0;
for (char ch : text) {
    if (ch == 'a') count++;
}
```

## 语法、API 与边界

find 找不到返回 std::string::npos（一个极大值），不能当 0 用；at 带边界检查，[] 不带。string 拼接用 + 或 append，频繁拼接可先 reserve。

```cpp
std::size_t position = text.find('n');
if (position != std::string::npos) {
    std::string piece = text.substr(0, position);
}
```

## 常见错误与实践建议

常见错误：把 npos 当有效位置、越界下标。统计类任务初始化计数器为 0 并只遍历一次。本课练习要求统计指定字符出现次数。
