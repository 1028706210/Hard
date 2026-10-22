---
id: cpp-oop-abstraction
title: C++ 数据抽象
concepts: [classes, inheritance]
objectives:
  - 用公开接口与隐藏实现分离关注点。
  - 依赖抽象接口编程而非具体实现细节。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-data-abstraction.html
source_snapshot_date: 2026-08-23
---

# C++ 数据抽象

## 概念定义与适用场景

数据抽象只向调用方暴露"做什么"（公开接口），隐藏"怎么做"（私有数据与内部算法）。调用方依赖接口编程，实现变化时不影响使用方，是低耦合设计的基础。

```cpp
class Sequencer {
public:
    virtual ~Sequencer() = default;
    virtual int next() = 0;  // 纯虚接口：只约定行为
};

class Doubler : public Sequencer {
public:
    explicit Doubler(int start) : value_(start) {}
    int next() override { value_ *= 2; return value_; }
private:
    int value_;
};
```

## 语法、API 与边界

纯虚函数（= 0）使类成为抽象类，不能实例化，只能通过指针或引用使用派生实现。抽象边界让测试可以用替身实现替换真实实现。

```cpp
Sequencer& seq = doubler;
int value = seq.next();  // 调用方不关心内部如何翻倍
```

## 常见错误与实践建议

不要把内部状态暴露为 public 让调用方参与维护（应提供受控操作）；接口粒度宜小而聚焦。本课练习要求依赖抽象接口完成序列生成。
