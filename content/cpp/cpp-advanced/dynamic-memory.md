---
id: cpp-advanced-dynamic-memory
title: C++ 动态内存
concepts: [memory]
objectives:
  - 使用 new/delete 与 new[]/delete[] 管理动态内存。
  - 理解智能指针的自动化释放价值。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-dynamic-memory.html
source_snapshot_date: 2026-08-23
---

# C++ 动态内存

## 概念定义与适用场景

new 在自由存储上分配对象并返回指针，delete 释放；new[]/delete[] 管理数组。动态内存适合运行期才确定大小的数据，代价是必须手动归还。

```cpp
int* values = new int[4]{1, 2, 3, 4};
int total = 0;
for (int i = 0; i < 4; i++) {
    total += values[i];  // 10
}
delete[] values;
```

## 语法、API 与边界

new[] 必须配对 delete[]（配错是未定义行为）；泄漏是忘记 delete，悬垂指针是 delete 后继续使用。现代 C++ 用 std::unique_ptr、std::make_unique 自动释放，自动管理所有权对应的释放责任，但仍需避免悬垂借用。

```cpp
#include <memory>

auto buffer = std::make_unique<int[]>(count);  // 离开作用域自动 delete[]
```

## 常见错误与实践建议

不要在异常路径上裸 new（提前 throw 导致泄漏）；优先 make_unique/make_shared 而非裸 new。本课练习要求手动 new[]/delete[] 完成一次分配-填充-释放闭环。

## 深入理解与完整示例

先区分对象生存期与存储期：裸指针变量离开作用域只销毁指针本身，不会自动释放它指向的动态对象。所有权必须清晰，借用对象的观察指针不能重复释放资源。动态长度优先 `std::vector`，独占单个对象优先 `std::unique_ptr`，确实需要共同拥有时才考虑 `std::shared_ptr`。

```cpp
#include <iostream>
#include <memory>
#include <utility>
int main() {
    auto owner = std::make_unique<int>(7);
    int* observer = owner.get();
    auto next_owner = std::move(owner);
    std::cout << (owner == nullptr) << ' ' << *next_owner << ' '
              << *observer << '\n';
}
```

输出 `1 7 7`：所有权移动了，对象地址没有因这次移动而变化。observer 的有效期取决于所指对象是否仍然存活；再次移动所有权不会使它失效。reset 或最终所有者析构并删除对象后，observer 才成为悬垂指针。release() 仅放弃所有权而不删除对象，调用方必须安排后续接管或释放。不要对仍由 unique_ptr 拥有的 get() 借用地址手动 delete。

资源获取即初始化（RAII）把释放责任绑定在对象析构上，正常返回和异常展开都可触发清理。智能指针解决其拥有对象的释放责任，不会消除所有悬垂别名、并发错误或 shared_ptr 循环引用。普通 new 分配失败通常抛出 `std::bad_alloc`，不是返回空指针；`std::nothrow` 形式才按对应约定返回空。不要使用未初始化的 new int[n] 元素；需要清零可使用值初始化或容器。当前练习保留手工分配配对训练，项目代码优先使用自动管理的容器和所有者。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/expr.new)。以上是本课程原创示例与讲解，条款用于核对语言语义。
