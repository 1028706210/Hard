---
id: csharp-capstone-language-quiz
title: C# 语言测验与结业实践
concepts: [types, control-flow, classes, collections, concurrency]
objectives:
  - 通过覆盖类型、异常、泛型、委托和并发的测验检查整条 C# 路线掌握情况。
  - 综合使用类、属性、泛型集合、委托与两个工作线程完成确定性的成绩汇总挑战。
prerequisites: [csharp-capstone-multithreading]
difficulty: advanced
experience_points: 50
source_url: https://www.runoob.com/csharp/csharp-quiz.html
source_snapshot_date: 2026-08-23
---

# C# 语言测验与结业实践

## 概念定义与适用场景

结业测验不是记忆孤立语法，而是检查能否把类型约束、错误路径、数据结构和执行顺序组合成可验证的程序。知识题用于辨析语言合同，代码题用于验证输入、分支和输出；综合挑战则要求不同模块的能力在同一条确定性数据流中协作。

```csharp
var answers = new[] { "B", "A", "C" };
var key = new[] { "B", "A", "B" };
var score = answers.Zip(key).Count(pair => pair.First == pair.Second);
Console.WriteLine(score);
```

## 语法、API 与边界

分级测试的答案必须来自有效选项，数量必须与题目数一致。综合程序先验证数量与每个分数的范围，再将列表划分成两个互不重叠的区间；工作线程分别生成局部结果，主线程等待后再计算总人数、及格人数与平均分。

```csharp
var results = new WorkerResult[2];
var first = new Thread(() => results[0] = new WorkerResult(120, 2));
var second = new Thread(() => results[1] = new WorkerResult(90, 1));
first.Start();
second.Start();
first.Join();
second.Join();
Console.WriteLine(results[0].Sum + results[1].Sum);

sealed record WorkerResult(long Sum, int Passed);
```

## 常见错误与实践建议

不要把公开样例的固定输出当成算法，也不要通过 `Sleep` 或线程打印顺序制造偶然通过。验证应覆盖空输入、数量不符、边界分数、全部及格和全部不及格。结业挑战中的线程只负责纯计算和写入自己的结果对象；所有格式化输出都在主线程完成，因此相同输入始终得到相同输出。
