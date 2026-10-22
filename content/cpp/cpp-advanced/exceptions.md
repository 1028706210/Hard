---
id: cpp-advanced-exceptions
title: C++ 异常处理
concepts: [exceptions]
objectives:
  - 使用 try/catch 捕获并区分标准异常类型。
  - 在解析失败路径上输出可理解的结果。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-exceptions-handling.html
source_snapshot_date: 2026-08-23
---

# C++ 异常处理

## 概念定义与适用场景

异常把"出错"与"处理"分离：throw 抛出对象沿调用链上抛，catch 按类型捕获。标准库解析函数（如 std::stoi）失败时抛 std::invalid_argument 或 std::out_of_range。

```cpp
#include <string>

try {
    int value = std::stoi("not-a-number");
} catch (const std::invalid_argument& error) {
    // 输入不是整数
}
```

## 语法、API 与边界

catch 子句按声明顺序匹配，应把具体类型放在 std::exception 之前；捕获引用避免切片复制。整数除零是未定义行为而非异常，需事先检查。

```cpp
try {
    int value = std::stoi(text, &pos);
} catch (const std::out_of_range& error) {
    // 数值超出 int 范围
}
```

## 常见错误与实践建议

不要用异常做正常流程控制（开销与可读性都差）；析构函数不应抛出异常。本课练习要求在解析失败时输出固定错误标记而不是崩溃。

## 深入理解与完整示例

异常路径也必须保持对象有效并释放已取得的资源。栈展开会按构造完成的逆序销毁需要清理的局部对象；裸指针所指对象不会因此自动删除。用 RAII 管理资源比在每一个 catch 里重复清理更可靠。

```cpp
#include <iostream>
#include <stdexcept>
#include <string>
int parse_all(const std::string& text) {
    std::size_t used = 0;
    int value = std::stoi(text, &used);
    if (used != text.size()) throw std::invalid_argument("trailing input");
    return value;
}
int main() {
    for (const std::string text : {"42", "42x", "99999999999999999999"}) {
        try {
            const int value = parse_all(text);
            std::cout << value << '\n';
        } catch (const std::invalid_argument&) {
            std::cout << "invalid\n";
        } catch (const std::out_of_range&) {
            std::cout << "range\n";
        }
    }
}
```

输出依次为 `42`、`invalid`、`range`。`stoi("42x")` 本身允许只解析前缀，本例通过 used 拒绝尾随字符；它也接受某些前导空白和符号，若协议禁止这些，需要额外定义并检查格式。

这个 parse_all 示例增加了整串解析合同；当前练习仍按 std::stoi 的前缀解析规则处理，并未要求上述尾随字符检查。例如练习输入 `42x` 时，std::stoi 得到 42，按题意输出两倍值 84；不能把补充案例的更严格规则直接当成旧练习要求。

按 `const std::exception&` 捕获可避免按值复制造成切片；catch 顺序从具体到一般。`throw;` 在处理器内保留原异常重新抛出；`throw error;` 会重新创建异常并可能丢失派生类型。基本保证要求失败后对象仍有效且不泄漏，强保证进一步要求失败不改变可观察状态；选哪一种要由操作契约说明。异常展开中析构函数再次向外抛出通常会终止程序，因此析构负责清理，应避免向外传播异常。

延伸核对：[C++ 标准草案相关条款](https://eel.is/c++draft/except.ctor)。以上是本课程原创示例与讲解，条款用于核对语言语义。
