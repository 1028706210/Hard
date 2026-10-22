---
id: csharp-foundations-environment
title: C# 开发环境
concepts: [variables, control-flow]
objectives:
  - 理解 SDK、项目与源文件的分工。
  - 用固定离线环境运行控制台代码。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-environment-setup.html
source_snapshot_date: 2026-08-23
---

# C# 开发环境

## 概念定义与适用场景

开发环境由固定 SDK、项目描述和源文件组成，可重复的版本配置比编辑器选择更重要。

```csharp
Console.WriteLine("SDK project ready");
```

## 语法、API 与边界

dotnet build 负责编译项目，dotnet run 负责启动；课程运行器使用固定离线模板且禁止自定义项目参数。

```csharp
var baseDir = AppContext.BaseDirectory;
Console.WriteLine(baseDir.Length > 0);
```

## 常见错误与实践建议

不要在线恢复未知包、修改 MSBuild 参数或依赖机器全局状态。 本课练习只使用 .NET 标准能力，固定从标准输入读取并向标准输出写入。
