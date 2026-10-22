---
id: cpp-oop-inheritance
title: C++ 继承
concepts: [inheritance, classes]
objectives:
  - 用 public 继承从基类派生新类并扩展行为。
  - 在派生类中扩展行为，并区分同名隐藏与虚函数重写。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-inheritance.html
source_snapshot_date: 2026-08-23
---

# C++ 继承

## 概念定义与适用场景

继承让派生类复用并扩展基类的成员：class Manager : public Employee 表示"是一种"关系，Manager 获得 Employee 的数据与函数，并可添加或重写行为。

```cpp
class Employee {
public:
    explicit Employee(int base) : base_(base) {}
    int salary() const { return base_; }
protected:
    int base_;
};

class Manager : public Employee {
public:
    Manager(int base, int bonus) : Employee(base), bonus_(bonus) {}
    int salary() const { return base_ + bonus_; }
private:
    int bonus_;
};
```

## 语法、API 与边界

需要给基类构造函数传参时，应在派生类初始化列表中显式指定；protected 成员对派生类可见、对外仍私有。public 继承保持"是一种"语义，private 继承表达"用…实现"，慎用。

```cpp
Manager lead(100, 50);
int total = lead.salary();  // 150
```

## 常见错误与实践建议

不要用继承复用代码而缺乏"是一种"关系（应改组合）；派生类重写基类方法时基类应声明 virtual（下节多态）。本课练习要求通过派生类扩展基类计算。

## 深入理解与完整示例

`public` 继承允许在需要基类引用的位置使用派生对象。基类的私有成员仍存在于对象中，但派生类不能直接访问；应通过基类提供的操作维护其约束。`protected` 扩大了派生类的访问范围，并不等于对外公开。`class` 未写继承方式时默认 private，`struct` 默认 public。

上一例 `salary()` 没有 virtual，因此 Manager 的同名函数是隐藏，不是运行期重写。下面同时展示二者差别：

```cpp
#include <iostream>
struct Employee {
    virtual ~Employee() = default;
    int level() const { return 1; }
    virtual int salary() const { return 100; }
};
struct Manager : Employee {
    int level() const { return 2; }
    int salary() const override { return 150; }
};
int main() {
    Manager manager;
    Employee& employee = manager;
    std::cout << manager.level() << ' ' << employee.level() << ' '
              << employee.salary() << '\n';
}
```

输出 `2 1 150`：非虚调用取决于表达式的静态类型，虚调用遵循实际对象的最终重写。`override` 能发现漏写 const、参数类型错误等签名不匹配。基类无需在每个派生重写中重复写 virtual。

构造时先初始化基类，再初始化成员，最后执行派生构造函数体；析构相反。未显式指定基类初始化时会尝试默认初始化，因此仅在没有可用默认构造等情况下必须显式传参。多继承可能引入名称歧义与菱形基类；先掌握单继承，多个能力优先用小接口组合。当前练习仍聚焦扩展基类计算。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/class.virtual)。以上是本课程原创示例与讲解，条款用于核对语言语义。
