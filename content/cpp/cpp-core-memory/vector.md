---
id: cpp-core-memory-vector
title: C++ vector 容器
concepts: [collections]
objectives:
  - 使用 std::vector 管理运行期长度的元素序列。
  - 用 push_back 与范围 for 完成动态收集与遍历统计。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-vector.html
source_snapshot_date: 2026-08-23
---

# C++ vector 容器

## 概念定义与适用场景

std::vector 是长度可变的连续序列容器，运行期按需增长，支持下标随机访问。相对定长数组，vector 适合元素个数在读取前未知的场景。

```cpp
#include <vector>

std::vector<int> scores;
scores.push_back(90);   // 追加元素
std::size_t count = scores.size();  // 1
```

## 语法、API 与边界

push_back 在尾部追加、size() 返回元素个数、下标访问不检查越界（at() 会抛出 std::out_of_range）。遍历优先用范围 for，空 vector 的遍历自然跳过。

```cpp
int total = 0;
for (int value : scores) {
    total += value;
}
```

## 常见错误与实践建议

不要在遍历时 push_back 改变长度（迭代器失效风险）；元素个数已知时可用 reserve 预留容量。本课练习用 vector 收集运行期输入并统计。

## 深入理解与完整示例

`size()` 是实际构造的元素个数，`capacity()` 是重新分配前可容纳的元素数；预留空间不是创建元素。`reserve(10)` 之后仍不能直接访问第一个不存在的元素，`resize(10)` 才会把长度改为十。

```cpp
#include <iostream>
#include <vector>
int main() {
    std::vector<int> values;
    values.reserve(8);
    std::cout << values.size() << ' ' << (values.capacity() >= 8) << '\n';
    values.resize(3, 2);
    values.push_back(5);
    int total = 0;
    for (const int value : values) total += value;
    std::cout << values.size() << ' ' << total << '\n';
}
```

输出为 `0 1`、`4 11`。capacity 的具体增长倍数不是标准保证，不能用“总是翻倍”设计程序。尾部追加的摊还复杂度为常数，但某一次重新分配仍可能移动或复制所有现有元素。

追加导致重分配时，旧元素指针、引用、迭代器全部失效；未重分配时尾后迭代器仍失效，不能靠 reserve 就在范围 for 中随意追加。只需生成扩展结果时，可先保存原长度并按索引读取、将新结果放进另一容器，或先完成遍历再追加。这里的整数副本遍历不涉及元素所有权；若要修改元素应明确使用 `auto&`，只读复杂对象可用 `const auto&`。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/vector.capacity)。以上是本课程原创示例与讲解，条款用于核对语言语义。
