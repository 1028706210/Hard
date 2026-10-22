---
id: cpp-capstone-random
title: C++ <random>
concepts: [functions, security]
objectives:
  - 会用 mt19937 + uniform_int_distribution 生成确定性序列。
  - 理解固定种子的可复现性与安全随机的边界。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-random.html
source_snapshot_date: 2026-08-23
---

# C++ <random>

## 概念定义与适用场景

`<random>` 把「随机源」与「分布」分开：mt19937 是确定性引擎，同一 seed 生成同一序列；uniform_int_distribution 把引擎输出映射到闭区间。测试里固定 seed 即可复现结果。

```cpp
#include <cstdio>
#include <random>

std::mt19937 engine(42);
std::uniform_int_distribution<int> spread(1, 100);
std::printf("%d\n", spread(engine));   // 每次运行都相同
```

## 语法、API 与边界

相同种子会使同一种 mt19937 引擎产生相同的原始序列；uniform_int_distribution 的具体映射算法不保证跨不同标准库实现得到相同序列，练习的复现范围是本平台固定工具链。mt19937 不是密码学安全生成器，即使用 random_device 播种也不会变成 CSPRNG。random_device 的随机源质量依赖实现，标准还允许在无法取得非确定随机数时使用伪随机引擎，不能仅凭类名断言适合令牌或密钥；安全场景应使用经过确认的系统或密码库 CSPRNG。distribution 每次调用会消耗引擎状态。

```cpp
std::random_device source;          // 随机源性质依赖实现
std::mt19937 sampled_engine(source()); // 仍是非密码学安全的伪随机引擎
```

## 常见错误与实践建议

常见错误：用 rand()%N（分布偏差、状态弱）、在循环内重复构造引擎。本课练习要求按读入种子输出前三个 1..100 随机数，同种子必须得到同输出。
