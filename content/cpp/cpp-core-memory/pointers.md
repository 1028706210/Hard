---
id: cpp-core-memory-pointers
title: C++ 指针
concepts: [pointers]
objectives:
  - 声明指针、取地址与解引用并理解三者关系。
  - 通过指针参数修改调用方数据。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-pointers.html
source_snapshot_date: 2026-08-23
---

# C++ 指针

## 概念定义与适用场景

指针是保存变量内存地址的值：& 取得对象地址，* 解引用访问所指向的对象。指针让函数能间接修改调用方数据，也是数组遍历与动态内存的基础。

```cpp
int value = 42;
int* ptr = &value;   // ptr 保存 value 的地址
*ptr = 7;            // 通过指针修改 value，现为 7
```

## 语法、API 与边界

指针必须指向有效对象后才能解引用；解引用空指针或未初始化指针是未定义行为。函数参数写成 int* 时，函数通过 *p 修改的是调用方的原对象。

```cpp
void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}
```

## 常见错误与实践建议

不要解引用未初始化或已失效的指针；现代 C++ 优先用引用传参，仅在需要可空或重新指向时用指针。new[] 分配的内存必须 delete[]，优先考虑容器避免手工管理。本课练习要求通过指针完成交换。

## 深入理解与完整示例

指针包含地址，不能仅靠“非空”证明对象仍活着。它可能指向局部变量、数组元素或动态对象；只有明确拥有由匹配 new 创建的对象时，才应负责 delete。指向普通局部变量的指针只是借用，不能释放。

```cpp
#include <iostream>
void increase(int* value) {
    if (value != nullptr) ++*value;
}
int main() {
    int first = 4, second = 9;
    const int* read_only = &first;
    read_only = &second;  // 可以改指向，不能通过它改对象
    int* const fixed = &first;
    *fixed = 6;          // 可以改对象，不能改 fixed 的指向
    increase(fixed);
    increase(nullptr);
    std::cout << first << ' ' << *read_only << '\n';
}
```

输出 `7 9`。`const int*` 与 `int* const` 分别限制所指对象和指针本身，也可组合成 `const int* const`。`nullptr` 具有专用类型，比整数 0 更明确。

指针加减只应在同一数组及其尾后位置范围内使用；尾后指针可比较、可作终止标记，不能解引用。返回局部对象地址、容器扩容后继续用旧元素地址、释放后再访问都会导致悬垂。把某一个指针设空不会修复其他别名。当前交换练习假定传入有效地址，真实接口还应说明是否允许空值；必须有对象时可选择引用参数。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/basic.compound)。以上是本课程原创示例与讲解，条款用于核对语言语义。
