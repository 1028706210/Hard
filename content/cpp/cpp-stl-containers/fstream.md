---
id: cpp-stl-containers-fstream
title: C++ <fstream>
concepts: [io]
objectives:
  - 会用 ofstream 写文件、ifstream 读文件。
  - 理解文件流作用域关闭与读取结束条件。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-fstream.html
source_snapshot_date: 2026-08-23
---

# C++ <fstream>

## 概念定义与适用场景

`<fstream>` 提供文件流：ofstream 写、ifstream 读、fstream 读写。构造时给路径即打开，析构自动关闭；`getline(ifstream, line)` 循环直到读取失败即为文件结束。

```cpp
#include <fstream>
#include <string>

{
    std::ofstream out("data.txt");
    out << "first" << std::endl;
    out << "second" << std::endl;
}
std::ifstream in("data.txt");
```

## 语法、API 与边界

ofstream 默认覆盖已存在文件；打开失败（路径不可写）时流为 fail 状态，写入静默丢弃，应检查。文件要在写入完成后才能读回——用花括号限定作用域或显式 close。

```cpp
std::string line;
int count = 0;
while (std::getline(in, line)) {
    count++;  // 逐行统计直到结束
}
```

## 常见错误与实践建议

常见错误：写完立即读同一仍打开的流、不检查打开失败、依赖 append 模式却没传 std::ios::app。建议小作用域 + 显式检查。本课练习要求写入两行再读回统计。
