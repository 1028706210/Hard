---
id: cpp-foundations-comments
title: C++ 注释
concepts: [tooling]
objectives:
  - 使用 // 与 /* */ 两种形式书写注释。
  - 理解注释在编译阶段的处理方式。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-comments.html
source_snapshot_date: 2026-08-23
---

# C++ 注释

## 概念定义与适用场景

注释是写给阅读者看的说明文字，编译器在词法处理阶段会把它整体剥离，因此注释不会生成任何指令，也不影响运行结果。单行注释以 // 开头直到行尾，块注释以 /* 开头、*/ 结束。

```cpp
// 计算两倍值：单行注释只覆盖本行
int doubled = value * 2;

/* 块注释可以
   跨越多行 */
```

## 语法、API 与边界

块注释不能嵌套：第一个 */ 就会结束整个注释。注释应当解释"为什么这样做"，而不是复述代码字面行为；调试期间可用注释临时屏蔽一段代码。

```cpp
int read_count = 0;
// std::cin >> read_count;  // 临时禁用的输入语句
/* 读取失败时保持 0，由后续逻辑统一处理 */
```

## 常见错误与实践建议

不要把关键说明写成与代码矛盾的过时注释；修改代码时同步修改注释。也不要试图用注释"关闭"一段含有块注释的代码（会因嵌套提前结束），此时应使用 #if 0 ... #endif。本课练习要求代码中包含说明用途的注释，并从标准输入读取数据输出结果。
