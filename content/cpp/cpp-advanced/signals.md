---
id: cpp-advanced-signals
title: C++ 信号处理
concepts: [signals]
objectives:
  - 用 signal() 注册处理器并理解 sig_atomic_t 标志位模式。
  - 用 raise() 在进程内触发信号验证处理路径。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-signal-handling.html
source_snapshot_date: 2026-08-23
---

# C++ 信号处理

## 概念定义与适用场景

信号是操作系统的异步软件中断：SIGINT（Ctrl+C）、SIGTERM（终止请求）等到达时中断正常流程，转而执行注册的处理器函数。signal() 把信号编号与处理器关联起来。

```cpp
#include <csignal>

volatile std::sig_atomic_t flagged = 0;

void handle_term(int) {
    flagged = 1;  // 处理器内只做最简单的置位
}

std::signal(SIGTERM, handle_term);
```

## 语法、API 与边界

处理器中只能访问 volatile sig_atomic_t 标志，不能做复杂操作或 IO；主流程轮询标志后决策。raise(SIGTERM) 在本进程内同步触发信号，适合验证处理路径。

```cpp
std::raise(SIGTERM);         // 触发已注册的处理器
if (flagged) { /* 响应终止请求 */ }
```

## 常见错误与实践建议

不要在信号处理器里调用 printf 或分配内存（异步不安全）；SIGKILL 无法被捕获。本课练习要求注册处理器后用 raise 验证标志位传播。
