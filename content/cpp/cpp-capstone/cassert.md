---
id: cpp-capstone-cassert
title: C++ <cassert>
concepts: [tooling]
objectives:
  - 会用 assert 表达内部不变量并理解 NDEBUG 影响。
  - 理解断言用于开发期检查而非输入校验。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-cassert.html
source_snapshot_date: 2026-08-23
---

# C++ <cassert>

## 概念定义与适用场景

assert 在条件为假时打印诊断并终止程序，用于开发期捕捉「不可能发生」的内部状态违例。定义 NDEBUG（常见于 release 构建）后断言整体消失，因此不能承担运行期输入校验。

```cpp
#include <cassert>
#include <iostream>
#include <vector>

std::vector<int> values{5, 1, 9};
assert(values.size() == 3);   // 内部不变量：读入数量与容器一致
```

## 语法、API 与边界

断言表达式不能有副作用（release 下不执行）；条件为假走 abort（异常退出码），不是可捕获的 C++ 异常。用户输入的合法性仍需显式检查与返回码。

```cpp
int n = static_cast<int>(values.size());
assert(n > 0);
```

## 常见错误与实践建议

常见错误：在 assert 里调用带副作用的函数、用 assert 校验 stdin。本课练习要求读取数据后先断言数量不变量再求最大值，输入范围错误仍用非零退出码拒绝。
