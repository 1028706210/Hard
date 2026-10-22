---
id: cpp-core-memory-functions
title: C++ 函数
concepts: [functions]
objectives:
  - 定义带参数与返回值的函数并正确调用。
  - 区分值传递与按引用传递对调用方数据的影响。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-functions.html
source_snapshot_date: 2026-08-23
---

# C++ 函数

## 概念定义与适用场景

函数把一段逻辑封装为可复用的命名单元，由返回类型、函数名、参数列表与函数体组成。声明（原型）给出签名，定义给出实现；调用时实参按签名匹配形参。

```cpp
int add(int a, int b) {
    return a + b;
}

int sum = add(3, 4);  // 7
```

## 语法、API 与边界

默认按值传递：形参是实参的副本，函数内修改不影响调用方。要修改调用方数据，需把形参声明为引用（int&）或指针。没有返回值的函数返回类型写 void；return 后的表达式类型必须与声明兼容。

```cpp
void double_it(int& value) {
    value *= 2;  // 通过引用修改调用方数据
}
```

## 常见错误与实践建议

不要声明了原型却忘记给出定义；返回局部变量的引用或指针是悬垂引用缺陷。参数较多时优先用结构体聚合，保持签名清晰。本课练习要求把核心计算放入独立函数完成。
