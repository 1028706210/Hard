---
id: cpp-oop-classes
title: C++ 类 & 对象
concepts: [classes, memory]
objectives:
  - 定义包含私有成员与公有成员函数的类。
  - 通过构造函数初始化对象并调用成员函数。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-classes-objects.html
source_snapshot_date: 2026-08-23
---

# C++ 类 & 对象

## 概念定义与适用场景

类是把数据（成员变量）与操作（成员函数）绑在一起的类型模板，对象是类的实例。class 默认私有、struct 默认公开；private 成员通常由本类成员函数或友元访问，public 成员构成对外接口。

```cpp
class Rect {
public:
    Rect(int width, int height) : width_(width), height_(height) {}
    int area() const { return width_ * height_; }
private:
    int width_;
    int height_;
};
```

## 语法、API 与边界

构造函数与类同名、无返回类型，成员初始化列表先于函数体执行；const 成员函数限制通过 this 修改非 mutable 数据成员。局部对象在作用域结束自动析构。

```cpp
Rect rect(3, 4);
int size = rect.area();  // 12
```

## 常见错误与实践建议

不要把数据成员全部设为 public 任意外部改写（破坏不变量）；成员命名加尾下划线或 m_ 前缀区分参数。本课练习要求用类封装数据并提供只读计算接口。

## 深入理解与完整示例

构造函数负责让对象从一开始就处于有效状态；成员初始化按类中声明顺序进行，不能靠调换初始化列表改变顺序。`explicit` 阻止单参数构造函数参与意外的隐式转换。`const` 成员函数限制通过 `this` 修改普通成员，但不代表它不会修改 `mutable` 成员或外部对象。

下面的计分对象拒绝非法初值、受控地增加分数，并允许在只读对象上查询。

```cpp
#include <iostream>
#include <stdexcept>
class Score {
    int value_;
public:
    explicit Score(int value) : value_(value) {
        if (value < 0 || value > 100) throw std::invalid_argument("invalid score");
    }
    void add(int delta) {
        if (delta < 0 || delta > 100 - value_) throw std::invalid_argument("invalid delta");
        value_ += delta;
    }
    int value() const { return value_; }
};
int main() {
    Score first(20);
    first.add(5);
    const Score copy = first;
    std::cout << first.value() << ' ' << copy.value() << '\n';
}
```

输出为 `25 25`。按值复制得到独立对象；这与 Java、C# 的类变量默认复制对象引用不同。此处只有整数成员，编译器生成的复制和析构行为已足够。持有资源时优先使用 `std::string`、容器或智能指针，让成员自行管理生命周期，这叫 Rule of Zero；不要给每个类机械地手写析构函数。需要自定义资源所有权时，再整体设计复制、移动与析构。

`private` 还允许友元访问，不能作为加密或安全隔离机制。当前练习验证封装计算；构造失败、复制语义和资源管理属于本节补充内容。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/class.base.init)。以上是本课程原创示例与讲解，条款用于核对语言语义。
