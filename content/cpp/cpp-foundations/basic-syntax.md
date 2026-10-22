---
id: cpp-foundations-basic-syntax
title: C++ 基本语法
concepts: [variables]
objectives:
  - 正确书写语句、标识符与字面量。
  - 从编译错误定位基础语法问题。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-basic-syntax.html
source_snapshot_date: 2026-08-23
---

# C++ 基本语法

## 概念定义与适用场景

基本语法规定标识符、字面量、语句与分号的书写规则，是编译器理解程序的前提。标识符区分大小写，由字母、数字和下划线组成且不能以数字开头。

```cpp
int count = 3;
std::string language = "cpp";
```

## 语法、API 与边界

双引号表示字符串字面量，单引号表示单个字符；每条语句以分号结束，块语句用花括号包裹。main 函数返回 int，惯例上 0 表示成功。

```cpp
char marker = '#';
std::cout << language << marker << count << std::endl;
```

## 常见错误与实践建议

不要遗漏分号、混淆大小写或使用未声明的名称；遇到编译错误先看第一条诊断，它往往最接近根因。本课练习固定从标准输入读取并向标准输出写入。
