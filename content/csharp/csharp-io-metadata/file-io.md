---
id: csharp-io-metadata-file-io
title: 文件输入输出
concepts: [io]
objectives:
  - 在当前工作目录内用相对路径完成写入与读回的完整闭环（File.WriteAllText/WriteAllLines 与 ReadAllLines/ReadLines）。
  - 区分覆盖写入与追加写入、一次性读取与惰性逐行读取，并说明文件操作必须限定在本次执行专用的临时工作目录内。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-file-io.html
source_snapshot_date: 2026-08-23
---

# 文件输入输出

## 概念定义与适用场景

`System.IO` 提供以文件为单位的读写工具：`File.WriteAllText/WriteAllLines` 一次写入并覆盖旧内容，`File.AppendAllText/AppendAllLines` 在末尾追加，`File.ReadAllText/ReadAllLines` 一次性读入，`File.ReadLines` 则惰性逐行返回。本课程平台中，程序只允许访问为本次执行创建的临时工作目录——即进程的当前工作目录，所有读写都必须使用相对路径。

```csharp
File.WriteAllText("greeting.txt", "你好，Hard\n");
var content = File.ReadAllText("greeting.txt");
Console.Write(content);
```

## 语法、API 与边界

`WriteAllLines` 默认用当前平台的换行符（Windows 上是 `\r\n`）分隔，`ReadAllLines/ReadLines` 能同时容忍 `\r\n` 与 `\n`，因此"写入再读回"的闭环不需要手工处理换行差异。`WriteAllText` 每次调用都会用新内容覆盖原文件，想保留历史必须改用追加系列 API 或自行拼接。大文件优先用 `File.ReadLines` 惰性枚举，避免 `ReadAllLines` 把整个文件载入内存。

```csharp
File.WriteAllLines("words.txt", new[] { "beta", "alpha" });
foreach (var line in File.ReadLines("words.txt"))
{
    Console.WriteLine(line);
}
```

## 常见错误与实践建议

两类高频错误：用绝对路径或 `..` 拼接去访问工作目录之外的文件——在课程平台里这既违反约定也不可靠；以及误以为追加调用是覆盖调用，导致旧数据残留。`StreamReader/StreamWriter` 这类需要 `Dispose` 的资源应始终放在 `using` 中，否则文件句柄可能延迟释放。再次强调：本平台的 Runner 是面向用户本人可信学习代码的本地执行环境，`TRUSTED_LOCAL_LEARNING_ONLY`，不是安全沙箱；练习中的文件操作一律限定在临时工作目录内，由练习或测试自己创建所需文件。
