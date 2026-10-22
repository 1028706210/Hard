---
id: cpp-core-memory-references
title: C++ 引用
concepts: [references]
objectives:
  - 声明引用并理解别名与改绑限制。
  - 通过引用参数让函数直接修改调用方数据。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-references.html
source_snapshot_date: 2026-08-23
---

# C++ 引用

## 概念定义与适用场景

引用是既有对象的别名：int& alias = value; 之后对 alias 的读写就是对 value 的读写。引用必须在声明时初始化且不能改绑到其他对象，相对指针更安全、语法更直接。

```cpp
int value = 10;
int& alias = value;
alias = 20;          // value 现为 20
```

## 语法、API 与边界

函数形参写成 int& 时按引用传递，函数内直接操作调用方对象，无需解引用语法。const int& 禁止通过该引用修改对象；对于 std::string 等较大的只读对象，const std::string& 可避免按值传递的复制。小型 int 通常直接按值传递即可。

```cpp
void double_it(int& value) {
    value *= 2;  // 直接修改调用方对象
}
```

## 常见错误与实践建议

不要返回局部变量的引用（悬垂引用）；引用不可为空，需要"可无对象"语义时改用指针。本课练习要求用引用参数的函数完成修改。

## 深入理解与完整示例

引用初始化后绑定到同一对象，之后的赋值是在改对象的值。引用不提供空值状态，但仍可能悬垂；因此“引用一定安全”是错误的。其生存期通常不会自动延长被引用对象的生存期。

```cpp
#include <iostream>
#include <string>
void append_mark(std::string& text) { text += '!'; }
std::size_t length(const std::string& text) { return text.size(); }
int main() {
    int first = 3, second = 8;
    int& alias = first;
    alias = second;
    second = 10;
    std::string message = "hi";
    append_mark(message);
    std::cout << first << ' ' << second << ' ' << length(message) << '\n';
}
```

输出 `8 10 3`，证明 alias 没有改绑到 second。输入参数用 `const T&` 可以借用较大对象且不允许通过该引用修改；需要修改用 `T&`；小型数值常直接按值传递。

局部 const 引用直接绑定临时对象时可延长该临时对象生存期，但返回函数内部局部变量的引用仍然错误；不要把这个规则推广为“所有间接引用都延寿”。`auto copy = container.front()` 复制元素，`auto& item = container.front()` 引用元素，前提是容器非空。`T&&` 是右值引用，移动操作是另一个主题；`std::move` 只产生相应的值类别转换，本身不保证发生资源搬移。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/dcl.ref)。以上是本课程原创示例与讲解，条款用于核对语言语义。
