---
id: csharp-oop-interfaces
title: 接口
concepts: [interfaces, polymorphism]
objectives:
  - 定义接口合同并用多个类分别实现同一接口。
  - 解释接口实现与类继承在复用方式上的差别。
prerequisites: [csharp-oop-polymorphism]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/csharp/csharp-interface.html
source_snapshot_date: 2026-08-23
---

# 接口

## 概念定义与适用场景

接口声明一组能力：实现类承诺提供这些成员。与继承"是一种"不同，接口表达"能做什么"，因此一个类可以同时实现多个互不相关的接口。

```csharp
interface ITransform
{
    string Apply(string text);
}

class UpperCaseTransform : ITransform
{
    public string Apply(string text) => text.ToUpperInvariant();
}
```

## 语法、API 与边界

本例无方法体的接口成员隐含 public；普通隐式实现必须是 public，也可以使用后文的显式接口实现。接口本身不保存实例字段；通过接口类型的变量调用成员，与通过基类引用一样产生运行期分派。实现接口的方法不需要 override 关键字。

```csharp
ITransform transform = new UpperCaseTransform();
Console.WriteLine(transform.Apply("hard"));
```

### 接口与抽象类如何选择

接口适合跨类型声明能力，抽象类适合在同一继承体系中共享状态、构造流程及部分实现。一个类可以实现多个接口，但只能继承一个类；struct 也能实现接口，却不能继承抽象类。先只需要调用能力时，定义一个小接口通常已足够，不必额外建立抽象基类。

传统接口中没有方法体的成员隐含 public，普通隐式实现必须是 public。另有“显式接口实现”：成员带接口限定名，不写 public，并且只能通过接口视图调用，适合同名能力需要不同实现的情况。

```csharp
var report = new Report();
IPrintable view = report;
Console.WriteLine(view.Print()); // report
// report.Print();               // 编译失败：只能通过接口访问

interface IPrintable
{
    string Print();
}

sealed class Report : IPrintable
{
    string IPrintable.Print() => "report";
}
```

现代 C# 的接口也能提供默认实现及部分静态成员，因此“接口永远没有实现”不准确；带实现的成员可以有其他访问级别。这些能力不改变接口不能包含实例字段、实例构造函数的边界。本章以传统实例合同为主，暂不展开默认接口成员的冲突规则或静态抽象接口成员。

调用接口成员仍会在运行期找到实际实现；接口变量只公开合同允许的成员。现有练习检查三种文本变换通过同一接口调用，显式实现与抽象类选型属于额外教学，不应当冒称已经被该练习覆盖。

## 常见错误与实践建议

实现类的成员若声明为 private 或忘了实现某个接口成员，会在编译期失败，而不是运行期才暴露。接口只描述合同，不应把状态塞进实现接口的类型层次里去模拟继承。本课练习用同一个接口变量承载三种实现，根据输入选择具体类。

技术核对（2026-10-21）：[Microsoft Learn：interfaces](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/interfaces)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
