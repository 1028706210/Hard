---
id: cpp-capstone-quiz
title: C++ 测验与路线结业
concepts: [types, exceptions, collections, concurrency]
objectives:
  - 通过覆盖类型、异常、容器与并发的测验检查整条 C++ 路线。
  - 综合输入校验、vector、双线程分片与格式化输出完成结业挑战。
prerequisites: [cpp-capstone-examples]
difficulty: advanced
experience_points: 50
source_url: https://www.runoob.com/cplusplus/cpp-quiz.html
source_snapshot_date: 2026-08-23
---

# C++ 测验与路线结业

## 概念定义与适用场景

结业不是背语法，而是把类型合同、错误路径、数据结构与执行顺序组合成可验证的程序：知识题辨析语言规则，代码题验证输入与输出合同，结业挑战要求多个模块的能力在同一条确定性数据流里协作。

```cpp
const char* key = "BACBC";
int score = 0;
for (int i = 0; i < 5; i++) {
    if (answers[i] == key[i]) score++;
}
```

## 语法、API 与边界

测验答案必须来自有效选项且数量与题数一致；结业挑战先校验 n 与每个分数范围，再把区间一分为二交给两个工作线程，主线程 join 后汇总输出。所有格式化输出都在主线程完成，结果与调度顺序无关。

```cpp
std::thread workers[2] = {std::thread(part, 0, half), std::thread(part, half, n)};
workers[0].join();
workers[1].join();
```

## 常见错误与实践建议

不要把公开样例的固定输出当算法，也不要靠线程打印顺序碰运气。验证覆盖空区间、边界分数、全部及格/不及格与数量不符。结业挑战线程只做纯计算并写回各自结果，join 后统一输出。
