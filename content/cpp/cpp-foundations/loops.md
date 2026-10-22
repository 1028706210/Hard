---
id: cpp-foundations-loops
title: C++ 循环
concepts: [control-flow]
objectives:
  - 使用 for、while 与 do-while 编写有限循环。
  - 识别并修复 off-by-one 边界错误。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-loops.html
source_snapshot_date: 2026-08-23
---

# C++ 循环

## 概念定义与适用场景

循环重复执行一段代码直到条件不再满足。for 把初始化、继续条件与每轮更新集中在一行，最适合计数循环；while 先判断后执行，do-while 至少执行一次。

```cpp
long long total = 0;
for (int i = 1; i <= 4; i++) {
    total += i;  // 累计 1+2+3+4 = 10
}
```

## 语法、API 与边界

循环边界是 off-by-one 高发区：需求"包含 n"时条件应写 i <= n，写 i < n 会少算一轮。累计值可能超出 int 范围时应使用 long long 保存，循环体内用 (long long) 提升参与乘法。

```cpp
int n = 100;
long long sum = 0;
int i = 1;
while (i <= n) {
    sum += i;
    i++;
}
```

## 常见错误与实践建议

不要写出条件永真的循环（忘记更新计数器）；循环体内修改循环变量时先确认终止条件仍会到达。本课练习要求用有限循环累计求和并以 long long 输出。
