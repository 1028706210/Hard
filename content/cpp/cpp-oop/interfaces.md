---
id: cpp-oop-interfaces
title: C++ 接口（抽象类）
concepts: [interfaces, polymorphism]
objectives:
  - 用纯虚函数定义接口契约。
  - 编写多个实现并通过统一接口调用。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-interfaces.html
source_snapshot_date: 2026-08-23
---

# C++ 接口（抽象类）

## 概念定义与适用场景

C++ 没有独立的 interface 关键字，常用带纯虚操作的抽象基类表达能力契约；是否包含状态和共同实现由设计决定。不同实现类各自提供具体行为。

```cpp
class Greeter {
public:
    virtual ~Greeter() = default;
    virtual std::string greet(const std::string& name) const = 0;
};

class FormalGreeter : public Greeter {
public:
    std::string greet(const std::string& name) const override {
        return "hello, " + name;
    }
};
```

## 语法、API 与边界

接口类不能实例化；具体类必须为全部纯虚函数提供最终的具体重写（可继承已有实现）才能创建对象。通过 Greeter& 或 Greeter* 使用实现，多个实现可在同一容器中混存（配合虚析构）。

```cpp
FormalGreeter formal;
Greeter& as_interface = formal;
std::string text = as_interface.greet("cpp");
```

## 常见错误与实践建议

纯接口通常保持小而聚焦；需要共享状态与实现时可采用抽象基类；接口名常以 -able 或描述能力命名。本课练习要求编写两个实现并经统一接口输出，模块挑战也挂在本课。

## 深入理解与完整示例

“接口”是设计角色，C++ 没有强制所有成员纯虚、禁止数据或实现的 interface 语法。常见的纯接口写法是公开虚析构加纯虚操作；抽象基类也可以提供状态与共同实现。前面的默认析构本身就已经是一个实现。应按调用方需要确定职责，而不是把设计惯例误记为语言限制。

```cpp
#include <iostream>
struct Reader {
    virtual ~Reader() = default;
    virtual int read() = 0;
};
struct FixedReader : Reader {
    int read() override { return 6; }
};
int twice(Reader& reader) { return reader.read() + reader.read(); }
int main() {
    FixedReader reader;
    std::cout << twice(reader) << '\n';
}
```

输出 `12`。twice 只依赖读取能力，替换实现不必修改调用方。抽象类不能直接创建完整对象；派生类若仍有未提供最终具体重写的纯虚函数，也仍是抽象类。具体实现可以来自中间基类，不要求每个末级类都把所有函数重新写一次。签名应注明参数、返回值和失败语义，“能编译”不代表不同实现具有相同业务契约。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/class.abstract)。以上是本课程原创示例与讲解，条款用于核对语言语义。
