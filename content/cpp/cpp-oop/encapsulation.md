---
id: cpp-oop-encapsulation
title: C++ 数据封装
concepts: [encapsulation, classes]
objectives:
  - 用私有成员与公有接口保护对象不变量。
  - 在修改操作中实施业务校验。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-data-encapsulation.html
source_snapshot_date: 2026-08-23
---

# C++ 数据封装

## 概念定义与适用场景

封装把数据设为私有、只经公有成员函数访问，使对象能在修改入口统一维护不变量（如余额不能为负）。外部无法绕过校验直接改写状态。

```cpp
class Account {
public:
    explicit Account(int balance) : balance_(balance) {}
    void deposit(int amount) { balance_ += amount; }
    bool withdraw(int amount);
    int balance() const { return balance_; }
private:
    int balance_;
};
```

## 语法、API 与边界

withdraw 这类操作返回 bool 表示成败，拒绝时对象状态不变；getter 标注 const 提供只读视图。不变量只在一处维护，修改规则时调用方无需改动。

```cpp
bool Account::withdraw(int amount) {
    if (amount > balance_) {
        return false;  // 保护不变量：拒绝非法修改
    }
    balance_ -= amount;
    return true;
}
```

## 常见错误与实践建议

不要为每个私有成员机械提供 setter（等于放弃封装）；校验失败要有明确信号（返回值或异常）而非静默吞掉。本课练习要求用封装账户拒绝非法取款。
