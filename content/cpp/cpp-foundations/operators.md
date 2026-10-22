---
id: cpp-foundations-operators
title: C++ 运算符
concepts: [operators]
objectives:
  - 掌握算术运算符的优先级与结合方向。
  - 理解整型溢出与除零等边界风险。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-operators.html
source_snapshot_date: 2026-08-23
---

# C++ 运算符

## 概念定义与适用场景

运算符把操作数组合成新值：算术（+ - * / %）、比较（== != < 等）、逻辑（&& || !）、位运算与赋值等。乘除取余的优先级高于加减，可用括号显式表达分组意图。

```cpp
int a = 2, b = 3, c = 4;
int value = a + b * c;   // 14：先乘后加
int grouped = (a + b) * c;  // 20：括号改变求值顺序
```

## 语法、API 与边界

当整数算术结果的类型为无符号类型时，按该类型范围进行模运算，超出范围会回绕；有符号整数算术溢出是未定义行为，不能依赖回绕结果。较窄的整数还可能先发生整型提升，判断时应看实际参与运算的类型。除法与取余的右操作数为 0 是未定义行为。&& 与 || 存在短路求值，右侧可能根本不执行。

```cpp
int safe_check(int divisor, bool enabled) {
    if (enabled && divisor != 0) {
        return 100 / divisor;
    }
    return 0;
}
```

## 常见错误与实践建议

不要依赖运算符优先级记忆写复杂表达式，优先加括号；比较写成赋值（= 与 ==）是高频笔误，可把常量放左侧。本课练习从标准输入读取三个整数并按优先级规则输出计算结果。
