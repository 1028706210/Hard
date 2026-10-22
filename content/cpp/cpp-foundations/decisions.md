---
id: cpp-foundations-decisions
title: C++ 判断
concepts: [control-flow]
objectives:
  - 使用 if/else 与 switch 编写分支逻辑。
  - 理解 switch 的 fall-through 与 break 的作用。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-decision.html
source_snapshot_date: 2026-08-23
---

# C++ 判断

## 概念定义与适用场景

判断语句依据条件选择执行路径：if 先求值条件（非 0 为真），else 捕捉相反情形；三元运算符 cond ? a : b 适合二选一取值；switch 按整型常量分派到匹配的 case。

```cpp
if (n > 0) {
    label = "positive";
} else if (n == 0) {
    label = "zero";
} else {
    label = "negative";
}
```

## 语法、API 与边界

switch 中匹配 case 后会一直执行到 break 或 switch 结束（fall-through），漏写 break 是经典缺陷；case 标签必须是编译期常量，default 处理未列举的值。

```cpp
switch (code) {
    case 1:
        result = "one";
        break;      // 缺失则继续落入 case 2
    case 2:
        result = "two";
        break;
    default:
        result = "other";
        break;
}
```

## 常见错误与实践建议

不要在分支中重复大段代码，提炼公共逻辑；条件里把 == 误写为 = 会把比较变成赋值。本课练习按输入整数的符号输出分类文本，模块挑战也挂在本课。
