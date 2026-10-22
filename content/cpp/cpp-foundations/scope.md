---
id: cpp-foundations-scope
title: C++ 变量作用域
concepts: [variables]
objectives:
  - 区分块作用域、函数作用域与全局作用域。
  - 理解内层同名变量对外层变量的遮蔽。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-variable-scope.html
source_snapshot_date: 2026-08-23
---

# C++ 变量作用域

## 概念定义与适用场景

作用域是名字可被引用的程序文本区域。花括号引入块作用域，块内声明的变量在块结束即销毁；函数外声明的变量具有全局作用域，从声明处到文件末尾可见。

```cpp
int global_count = 100;  // 全局作用域

void demo() {
    int local_count = 1;  // 仅在 demo 内可见
}
```

## 语法、API 与边界

内层块可以声明与外层同名的变量，此时内层引用遮蔽外层声明；离开内层块后外层名字恢复可见。同名遮蔽容易造成误读，必要时用更具体的名字区分。

```cpp
int value = 10;
{
    int value = 20;      // 遮蔽外层 value
    // 此处 value 为 20
}
// 此处 value 恢复为 10
```

## 常见错误与实践建议

不要在块结束后引用块内变量（已销毁）；减少全局变量的使用，因为任何函数都能修改它，使数据流向难以追踪。本课练习要求把中间结果保存在嵌套块的局部变量中完成计算。
