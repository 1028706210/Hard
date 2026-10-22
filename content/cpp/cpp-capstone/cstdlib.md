---
id: cpp-capstone-cstdlib
title: C++ <cstdlib>
concepts: [operators]
objectives:
  - 会用 strtol 配合 endptr 严格解析整数。
  - 理解 strtol 与 atoi 的失败可判定性差异。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-cstdlib.html
source_snapshot_date: 2026-08-23
---

# C++ <cstdlib>

## 概念定义与适用场景

`<cstdlib>` 的 strtol 把字符串转 long，并通过 endptr 报告「停在哪里」：指向结尾说明完整解析，否则存在非法尾巴。atoi 失败只返回 0，无法与真 0 区分。

```cpp
#include <cstdlib>
#include <iostream>

const char* text = "123";
char* end = nullptr;
long value = std::strtol(text, &end, 10);
if (end == text || *end != '\0') {
    std::cout << "invalid" << std::endl;
}
```

## 语法、API 与边界

第三参是基数（10 十进制、0 自动探测）；解析溢出返回 LONG_MAX/LONG_MIN 并置 errno=ERANGE。空串或首字符非法时 end 不前进。

```cpp
long result = std::strtol("  42x", &end, 10);   // result=42, *end=='x'
```

## 常见错误与实践建议

常见错误：忽略 endptr 把 "12x" 当 12、用 atoi 做输入校验。本课练习要求用 strtol 逐个解析整数 token，任何非法 token 整体拒绝。
