---
id: cpp-oop-polymorphism
title: C++ 多态
concepts: [polymorphism, inheritance]
objectives:
  - 通过虚函数与基类指针实现运行期多态。
  - 理解重写与隐藏的区别及 override 的作用。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-polymorphism.html
source_snapshot_date: 2026-08-23
---

# C++ 多态

## 概念定义与适用场景

多态让同一调用按对象实际类型分派：基类方法声明 virtual 后，经由基类指针或引用调用时执行派生类的重写版本。这是容器中混合存放多种派生对象并统一处理的基础。

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual int area() const { return 0; }
};

class Square : public Shape {
public:
    explicit Square(int side) : side_(side) {}
    int area() const override { return side_ * side_; }
private:
    int side_;
};
```

## 语法、API 与边界

override 显式标记重写，签名不匹配时编译报错；基类析构函数应为 virtual，否则经基类指针 delete 派生对象是未定义行为。非虚函数按静态类型分派（隐藏而非重写）。

```cpp
Shape* shape = new Square(3);
int size = shape->area();   // 9：运行期分派
delete shape;
```

## 常见错误与实践建议

不要忘记基类虚析构；不要期望非虚函数表现出多态。优先用 unique_ptr 管理多态对象避免手工 delete。本课练习要求用基类指针统一调用不同派生类实现。

## 深入理解与完整示例

多态依赖对象仍然是派生对象。把派生对象按值复制到基类会丢失派生部分，称为对象切片；指针或引用不执行这种复制。需要让容器拥有不同派生对象时，用 `std::unique_ptr<Base>` 表达唯一所有权，并提供合适的虚析构函数。

```cpp
#include <iostream>
#include <memory>
struct Instrument {
    virtual ~Instrument() = default;
    virtual int notes() const { return 1; }
};
struct Piano : Instrument {
    int notes() const override { return 88; }
};
int main() {
    Piano piano;
    const Instrument& view = piano;
    Instrument sliced = piano;
    std::unique_ptr<Instrument> owner = std::make_unique<Piano>();
    std::cout << view.notes() << ' ' << sliced.notes() << ' '
              << owner->notes() << '\n';
}
```

输出 `88 1 88`。不要把 `std::vector<Base>` 当成保留派生类型的多态容器。抽象基类则根本不能按值创建或复制成独立对象。

构造和析构期间的虚调用只分派到当前正在构造或析构的类层级，不会调用尚未构造或已经析构的派生部分。也不要从这些阶段依赖纯虚调用。`final` 可以禁止进一步重写或派生，它不替代正确的接口设计。运行期多态适合可替换行为；类型在编译期已经确定时，普通函数和模板往往更直接。当前练习测试虚调用，不自动证明切片与所有权知识已经掌握。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/class.cdtor)。以上是本课程原创示例与讲解，条款用于核对语言语义。
