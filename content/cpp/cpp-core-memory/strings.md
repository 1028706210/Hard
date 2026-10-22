---
id: cpp-core-memory-strings
title: C++ 字符串
concepts: [strings]
objectives:
  - 使用 std::string 与 getline 处理含空格文本。
  - 完成拼接、取长度与按下标反转等操作。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-strings.html
source_snapshot_date: 2026-08-23
---

# C++ 字符串

## 概念定义与适用场景

std::string 是可变长度的字符序列，支持 + 拼接、size()/length() 取长度、下标访问与 == 比较，自动管理内存。C 风格字符串（char 数组）需要手动处理结尾 '\0'，现代代码优先 std::string。

```cpp
std::string name = "hard";
std::string full = name + "-cpp";  // "hard-cpp"
std::size_t length = full.size();  // 8
```

## 语法、API 与边界

>> 读取到空白即停，含空格的整行文本要用 std::getline(std::cin, line)。下标访问越界同样是未定义行为；需要 C 接口时用 c_str() 获取只读指针。

```cpp
std::string reversed;
for (std::size_t i = line.size(); i > 0; i--) {
    reversed += line[i - 1];
}
```

## 常见错误与实践建议

不要用 < 比较无符号 size() 与有符号 int 循环变量（会触发符号转换警告甚至死循环）；空行也是合法输入。本课练习读取整行文本并输出反转结果。
