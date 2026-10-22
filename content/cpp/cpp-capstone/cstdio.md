---
id: cpp-capstone-cstdio
title: C++ <cstdio>
concepts: [io]
objectives:
  - 会用 printf 格式说明符做定宽输出。
  - 理解 scanf 返回值与解析失败的处理。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-cstdio.html
source_snapshot_date: 2026-08-23
---

# C++ <cstdio>

## 概念定义与适用场景

`<cstdio>` 提供printf/scanf 族 C 风格 IO。定宽、补零、定点小数这类格式化用格式说明符一次完成，比手写循环更直接；scanf 的返回值是成功解析的项目数，是判错的依据。

```cpp
#include <cstdio>

int value = 42;
std::printf("%05d\n", value);      // 00042
std::printf("hex=%x\n", value);    // hex=2a
```

## 语法、API 与边界

%05d 表示宽度 5、不足补 0；%d/%u/%lld 必须与实参类型严格匹配，错配是未定义行为。scanf 返回 EOF（输入结束）或成功项数，检查「不等于期望值」即失败。

```cpp
int parsed = 0;
if (std::scanf("%d", &parsed) != 1) {
    return 1;   // 解析失败
}
```

## 常见错误与实践建议

常见错误：忽略 scanf 返回值、用 %d 读 long long。C++ 项目里 iostream 更安全，cstdio 适合定宽格式化场景。本课练习要求把整数输出为 5 位补零形式。
