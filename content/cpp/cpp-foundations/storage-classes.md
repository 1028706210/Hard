---
id: cpp-foundations-storage-classes
title: C++ 存储类
concepts: [memory]
objectives:
  - 理解 static 局部变量的生命周期与一次初始化语义。
  - 认识现代 C++ 中 auto 的类型推导含义。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-storage-classes.html
source_snapshot_date: 2026-08-23
---

# C++ 存储类

## 概念定义与适用场景

存储类描述变量的生命周期、链接性与初始化方式。函数内声明的 static 局部变量只在程序启动时初始化一次，存活到程序结束，但名字仍只在函数内可见；auto 在现代 C++ 中表示从初始化表达式推导类型。

```cpp
int next_id() {
    static int counter = 0;  // 仅初始化一次
    return ++counter;        // 跨调用保留状态
}
```

## 语法、API 与边界

static 局部变量在两次调用之间保留值，适合实现计数器、缓存等函数内状态；auto 必须有初始化表达式，否则无法推导。extern 用于跨编译单元共享全局变量声明。

```cpp
auto count = 10;      // int
auto ratio = 2.5;     // double
extern int shared;    // 在别处定义
```

## 常见错误与实践建议

不要用 static 局部变量保存需要并发访问的状态（多线程下无保护）；auto 推导会丢弃引用与顶层 const，需要保留时显式写 auto&。本课练习要求用 static 局部计数器统计函数调用次数。
