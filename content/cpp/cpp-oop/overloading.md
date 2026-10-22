---
id: cpp-oop-overloading
title: C++ 重载运算符和重载函数
concepts: [operator-overloading, operators]
objectives:
  - 定义同名不同参的重载函数并理解解析规则。
  - 为自定义类型重载运算符获得自然语法。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-overloading.html
source_snapshot_date: 2026-08-23
---

# C++ 重载运算符和重载函数

## 概念定义与适用场景

函数重载允许同名函数按参数个数或类型区分，编译器依据实参选择最匹配版本。运算符重载把 +、*、== 等运算符扩展到自定义类型，使对象运算获得与内建类型一致的语法。

```cpp
int triple(int value) { return value * 3; }

class Vec2 {
public:
    Vec2(int x, int y) : x_(x), y_(y) {}
    Vec2 operator*(int k) const { return Vec2(x_ * k, y_ * k); }
    int x() const { return x_; }
    int y() const { return y_; }
private:
    int x_;
    int y_;
};
```

## 语法、API 与边界

重载区分不看返回类型，仅看参数；运算符重载可以是成员（左操作数是本类）或非成员（支持左侧转换）。&&、|| 重载后失去短路语义，逗号与取地址不应重载。

```cpp
Vec2 v(1, 2);
Vec2 scaled = v * 3;   // (3, 6)
```

## 常见错误与实践建议

不要让重载运算符的行为违背直觉（operator+ 做减法）；对称运算优先非成员实现。本课练习要求为自定义类型重载运算符完成计算。
