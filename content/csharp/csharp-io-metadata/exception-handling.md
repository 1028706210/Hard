---
id: csharp-io-metadata-exception-handling
title: 异常处理
concepts: [exceptions]
objectives:
  - 使用 try/catch/finally 包裹可失败操作，按 DivideByZeroException、OverflowException、FormatException 等具体异常分别给出安全、可理解的兜底行为。
  - 解释 checked 上下文与整数溢出异常的关系，避免笼统捕获 Exception 掩盖程序缺陷或把内部细节泄漏给调用方。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-exception-handling.html
source_snapshot_date: 2026-08-23
---

# 异常处理

## 概念定义与适用场景

异常是运行期错误的载体：解析失败、除以零、数值溢出等。`try` 包住可能失败的操作，`catch` 按异常类型分别响应，`finally` 承接无论成败都必须执行的清理。目标是让程序在出错时给出安全、可理解的结果，而不是崩溃或静默吞错。

```csharp
try
{
    var value = int.Parse(text);
    Console.WriteLine(value / divisor);
}
catch (FormatException)
{
    Console.WriteLine("输入不是整数");
}
catch (DivideByZeroException)
{
    Console.WriteLine("除数不能为零");
}
```

## 语法、API 与边界

catch 子句按书写顺序匹配，因此必须把具体异常放在 `catch (Exception)` 之前，否则笼统分支会拦截一切、让具体处理永远失效。默认情况下整数算术不抛溢出异常而是静默回绕；只有放进 `checked` 上下文，`+`、`-`、`*` 才会在溢出时抛出 `OverflowException`。`finally` 即使 `try` 中已经 `return` 也会执行，适合关闭文件与释放资源；不能用它返回业务结果。

```csharp
try
{
    checked
    {
        var sum = left + right;
        Console.WriteLine(sum);
    }
}
catch (OverflowException)
{
    Console.WriteLine("结果超出 int 范围");
}
```

## 常见错误与实践建议

最常见的错误是 `catch (Exception)` 一把抓：它把真正的程序缺陷（空引用、越界）和预期的输入问题混在一起，掩盖了 bug。其次是把异常对象的完整消息或堆栈直接输出给最终用户——这可能暴露内部路径等敏感细节，正确做法是输出简短、稳定的提示文本。异常处理是兜底手段而不是流程控制：能用 `int.TryParse` 提前判断的输入，就不必依赖抛异常来分支。本课练习要求对格式错误、除零和溢出分别捕获并统一输出稳定提示，同时保持退出码语义清晰。
