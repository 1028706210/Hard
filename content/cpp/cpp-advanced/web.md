---
id: cpp-advanced-web
title: C++ Web 编程
concepts: [web]
objectives:
  - 理解 CGI 模型下服务器如何调用 C++ 程序并交换数据。
  - 按 HTTP 合同输出响应头与正文。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-web-programming.html
source_snapshot_date: 2026-08-23
---

# C++ Web 编程

## 概念定义与适用场景

CGI（Common Gateway Interface）把 Web 请求交给外部程序处理：服务器以环境变量传递元信息（如 QUERY_STRING），POST 正文经标准输入进入程序，程序向标准输出写回完整 HTTP 响应。C++ 程序因此只需关心 stdin/stdout 合同即可参与 Web 交互。

```cpp
#include <iostream>
#include <string>

int main() {
    std::string query = "name=ada";  // 实际来自 QUERY_STRING 环境变量
    std::string name = query.substr(query.find('=') + 1);
    std::cout << "Content-Type: text/plain\n\n";
    std::cout << "hello, " << name << std::endl;
    return 0;
}
```

## 语法、API 与边界

响应必须先输出头（如 `Content-Type: text/plain`），再输出一个空行，之后才是正文；缺少空行会被服务器当作坏响应。查询串是 `key=value` 以 `&` 连接的文本，解析时要处理键不存在或值缺失的情形。

```cpp
std::string query = "a=1&b=2";
std::size_t amp = query.find('&');
std::string first = query.substr(0, amp);      // "a=1"
std::string second = query.substr(amp + 1);    // "b=2"
```

## 常见错误与实践建议

常见错误：忘记头后的空行、直接拼接未校验的输入导致响应格式破坏。建议把「解析—校验—输出」分开，任何一步失败就非零退出而不是输出半截响应。本课练习要求按合同解析查询串并输出带头的响应。
