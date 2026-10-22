---
id: cpp-stl-containers-vector
title: C++ <vector>
concepts: [collections]
objectives:
  - 会用 push_back 动态追加元素并读取 size/front/back。
  - 理解 vector 连续存储与按需扩容。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-vector.html
source_snapshot_date: 2026-08-23
---

# C++ <vector>

## 概念定义与适用场景

`std::vector<T>` 是动态数组：元素连续存储，push_back 尾部追加，容量不足时自动扩容（增长倍数由实现决定，重分配使迭代器失效）。它是默认容器首选——按下标随机访问 O(1)。

```cpp
#include <iostream>
#include <vector>

std::vector<int> values;
values.push_back(10);
values.push_back(20);
int count = static_cast<int>(values.size());
```

## 语法、API 与边界

front()/back() 访问首尾，空容器上调用是未定义行为；size() 返回元素个数（无符号），与有符号运算时注意混用警告。扩容会使指向元素的指针与迭代器失效，追加循环里不要保存旧迭代器。

```cpp
if (!values.empty()) {
    std::cout << values.front() << " " << values.back() << std::endl;
}
```

## 常见错误与实践建议

常见错误：空容器取 front、size() 与 int 比较的符号警告、循环里持有失效迭代器。建议先判 empty 再取首尾。本课练习要求尾插后输出个数、首元素与尾元素。

## 深入理解与完整示例

掌握追加后，还需要区分删除与失效。erase 会移动后续元素，返回被删元素之后的新位置；循环删除时必须接住这个返回值，不能继续递增旧迭代器。

```cpp
#include <iostream>
#include <vector>
int main() {
    std::vector<int> values{1, 2, 3, 4, 5};
    for (auto it = values.begin(); it != values.end();) {
        if (*it % 2 == 0) it = values.erase(it);
        else ++it;
    }
    for (int value : values) std::cout << value << ' ';
    std::cout << '\n';
}
```

输出 `1 3 5`。erase 会使删除位置及之后的引用和迭代器失效；尾后迭代器也包括在内。没有重新分配的 insert 也会使插入位置及之后的引用和迭代器失效；发生重新分配则全部失效。`clear()` 清空元素，不保证释放 capacity；`shrink_to_fit()` 也只是非强制的收缩请求。

vector 的中间插入和删除通常需要线性移动，但不能据此自动断言链表一定更快：查找位置、缓存局部性和分配成本都影响实际性能。先选择符合访问方式的简单容器，再用代表性数据测量。当前练习仍是尾插与首尾查询，删除循环是补充案例。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/vector.modifiers)。以上是本课程原创示例与讲解，条款用于核对语言语义。
