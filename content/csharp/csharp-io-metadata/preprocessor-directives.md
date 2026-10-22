---
id: csharp-io-metadata-preprocessor-directives
title: 预处理器指令
concepts: [preprocessor-directives]
objectives:
  - 解释 #if/#else/#endif 在编译期裁剪代码的行为，并手工模拟嵌套条件编译的包含结果。
  - 区分编译期指令（#define、#if、#region）与运行期分支的不同效果，识别未闭合结构导致的编译失败。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-preprocessor-directives.html
source_snapshot_date: 2026-08-23
---

# 预处理器指令

## 概念定义与适用场景

预处理器指令是写给编译器的标记，以 `#` 开头并独占一行。它们在编译阶段生效，用来选择哪些代码参与编译、组织编辑器折叠或调整诊断行为。典型场景是让调试输出只在定义了 `DEBUG` 符号的构建中出现，而为正式构建留下干净的程序。

```csharp
#define TRACE_ENABLED

#if TRACE_ENABLED
Console.WriteLine("构建时启用了跟踪输出");
#else
Console.WriteLine("正式构建");
#endif
```

## 语法、API 与边界

`#define` 必须出现在该文件的任何普通 C# 代码之前，包括 using 指令之前；前面可以有空白、注释或其他预处理器指令，定义的符号只在当前源文件内有效，作用范围是编译单元而不是整个项目。`#if` 可以嵌套，`#else` 与最近一个未闭合的 `#if` 配对；嵌套块即使处于被裁剪的分支里，也必须保持 `#if/#endif` 配对完整，否则编译器报结构错误。`#region/#endregion` 只影响编辑器折叠，完全不改变程序行为。

```csharp
#if TRIAL
#if EXPORT_ALLOWED
Console.WriteLine("试用版且允许导出");
#endif
#else
Console.WriteLine("完整版");
#endif
```

上面 `TRIAL` 未定义时，整段嵌套块都会被裁剪，输出只有"完整版"。

## 常见错误与实践建议

初学者最常见的两类错误：把 `#if` 当成运行期 `if` 来写业务逻辑，导致发布行为与调试行为差异难以追踪；以及在被禁用的分支里遗漏配对的 `#endif`，让整个文件无法编译。经验法则是：条件编译只用于构建差异（平台、调试开关），数据相关的分支一律交给运行期 `if`。判断一段嵌套条件编译最终留下哪些代码，方法是按栈逐层推演：从外层向内层记录每层当前分支是否被选中，只有所有层都选中的内容才参与编译，所有指令行本身都会从结果中消失。

技术核对（2026-10-21）：[Microsoft Learn：preprocessor-directives](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/preprocessor-directives)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
