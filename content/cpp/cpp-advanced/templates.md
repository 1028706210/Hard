---
id: cpp-advanced-templates
title: C++ 模板
concepts: [generics]
objectives:
  - 编写函数模板实现类型无关算法。
  - 理解编译期实例化与显式指定模板实参。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-templates.html
source_snapshot_date: 2026-08-23
---

# C++ 模板

## 概念定义与适用场景

模板以类型为参数生成代码：函数模板一份逻辑适配多种类型，类模板生成类型安全的容器（vector 就是类模板）。编译器按实际使用的类型在编译期实例化。

```cpp
template <typename T>
T max_of(T a, T b) {
    return a > b ? a : b;
}

int big = max_of(3, 9);        // 实例化为 int 版本
double wide = max_of(1.5, 2.5);  // 实例化为 double 版本
```

## 语法、API 与边界

模板实参可推导（按函数参数）也可显式指定（max_of<double>(...)）；类型参数要求支持所用运算，不满足时编译失败并给出实例化错误。

```cpp
template <typename T>
T clamp_to(T value, T low, T high) {
    return value < low ? low : (value > high ? high : value);
}
```

## 常见错误与实践建议

不要为少数类型写宏替代模板（宏无类型检查）；模板定义需对使用方可见（常置于头文件）。本课练习要求用函数模板完成比较计算。

## 深入理解与完整示例

模板不是在运行时把对象都转换成某一种共同基类。它把类型差异留到编译期检查，因此同一逻辑可以得到多个具体实例。模板只有在实际使用相应操作时才要求类型满足这些操作，并非“对任何类型都有效”。

```cpp
#include <iostream>
#include <string>
template<class T>
class Box {
    T value_;
public:
    explicit Box(const T& value) : value_(value) {}
    const T& get() const { return value_; }
};
template<class T>
T larger(T first, T second) { return first < second ? second : first; }
int main() {
    Box<std::string> label("orbit");
    std::cout << larger(3, 7) << ' ' << larger<double>(3, 2.5)
              << ' ' << label.get() << '\n';
}
```

输出 `7 3 orbit`。`larger(3, 2.5)` 的两个参数会推导出冲突的 T，因此这里显式选择 double。模板不能代替理解数值转换；把 double 强制选成 int 可能丢失小数。

函数模板与类模板分别生成函数和类型；不同 `Box<T>` 是不同类型。一般将模板定义放在头文件，供实例化处看到；显式实例化是可选的工程组织方式。C++20 的 concepts/requires 可把“可比较”等要求写出来，但本课程既有运行练习按当前项目工具链标准执行，本节不要求升级编译标准。练习覆盖函数模板比较，类模板与约束需要另做练习才能评估。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/temp)。以上是本课程原创示例与讲解，条款用于核对语言语义。
