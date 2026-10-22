---
id: cpp-advanced-files
title: C++ 文件和流
concepts: [io]
objectives:
  - 使用 ofstream/ifstream 完成相对路径文件写读回。
  - 检查流状态并处理打开失败。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-files-streams.html
source_snapshot_date: 2026-08-23
---

# C++ 文件和流

## 概念定义与适用场景

文件流把磁盘文件接入流接口：ofstream 写、ifstream 读、fstream 读写。文本模式按行处理，适合配置与记录；构造时传文件名即自动打开，析构时自动关闭。

```cpp
#include <fstream>

std::ofstream out("words.txt");
out << "hard-cpp" << std::endl;

std::ifstream in("words.txt");
std::string line;
std::getline(in, line);  // "hard-cpp"
```

## 语法、API 与边界

文件操作应使用相对路径且仅访问当前工作目录（一次性临时工作区），禁止绝对路径与 .. 逃逸。打开失败时流处于失败态，可用 is_open() 检查后再读写。

```cpp
std::ifstream missing("absent.txt");
if (!missing.is_open()) {
    // 明确处理打开失败，而不是继续读取
}
```

## 常见错误与实践建议

不要忽略流失败态继续读（得到旧值或死循环）；写读同一文件先关闭或分开对象。文件 IO 是可核验的写读闭环：写入的内容应能读回并输出比对。本课练习要求写入后读回输出。
