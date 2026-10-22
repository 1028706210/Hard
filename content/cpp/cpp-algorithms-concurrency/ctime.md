---
id: cpp-algorithms-concurrency-ctime
title: C++ <ctime>
concepts: [types]
objectives:
  - 会用 std::time_t 与 std::gmtime 把秒数转为 UTC 时间分量。
  - 理解 tm 结构各字段的含义与起点。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-ctime.html
source_snapshot_date: 2026-08-23
---

# C++ <ctime>

## 概念定义与适用场景

`<ctime>` 处理日历时间：std::time_t 存秒数（自 1970-01-01 UTC 起），std::gmtime 把它转成 std::tm 结构（含小时 tm_hour、分钟、日期等分量），mktime 反向归一化。跨时区统一用 UTC 最稳。

```cpp
#include <ctime>
#include <iostream>

std::time_t moment = 3661;               // 1970-01-01 01:01:01 UTC
std::tm* utc = std::gmtime(&moment);
int hour = utc->tm_hour;                 // 1
```

## 语法、API 与边界

gmtime 返回指向静态缓冲区的指针（单线程使用安全，多线程要 gmtime_s/gmtime_r）；tm_year 从 1900 起计、tm_mon 从 0 起计，输出年份要 +1900、月份 +1。

```cpp
int year = utc->tm_year + 1900;
int month = utc->tm_mon + 1;
```

## 常见错误与实践建议

常见错误：忘 +1900/+1 直接输出年份月份、多线程共用 gmtime 静态缓冲。秒数换算时注意 86400 = 一天。本课练习要求输出秒数对应的 UTC 小时。
