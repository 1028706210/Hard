---
id: csharp-io-metadata-reflection
title: 反射（Reflection）
concepts: [reflection, classes]
objectives:
  - 使用 typeof、GetType 与 BindingFlags 在运行期枚举本程序集内类型的公共属性与方法元数据。
  - 区分编译期类型与运行期类型，并把反射限制在教学检查范围内（检查自己程序集的元数据，而非逃逸、绕过或宿主扫描工具）。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-reflection.html
source_snapshot_date: 2026-08-23
---

# 反射（Reflection）

## 概念定义与适用场景

反射让程序在运行期观察类型的元数据：类型有哪些属性、方法、参数，特性里写了什么。它支撑序列化器、依赖注入容器这类基础设施，也能用于在运行期读取自定义特性；编译器和源码生成器还可在构建时分析特性。本课程中反射的教学范围是检查自己程序集内的类型元数据——它是观察工具，不是逃逸封装、绕过限制或扫描宿主环境的手段。

```csharp
using System.Reflection;

foreach (var property in typeof(Plane).GetProperties())
{
    Console.WriteLine(property.Name);
}
```

## 语法、API 与边界

`typeof(具体类型名)` 根据源码中的类型名取得 Type 对象，`typeof(T)` 则取得当前泛型类型实参的 Type 对象，`instance.GetType()` 返回运行期实际类型，两者可能不同（例如变量声明为 object）。`GetProperties/GetMethods` 默认返回公共成员，包括继承来的；用 `BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly` 可只取本类型声明的实例成员。注意：自动属性会生成 `get_Xxx/set_Xxx` 访问器方法，它们会出现在 `GetMethods` 结果里，用 `m.IsSpecialName` 排除。

```csharp
using System.Reflection;

var methods = typeof(Plane).GetMethods(
    BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly)
    .Where(m => !m.IsSpecialName)
    .Select(m => m.Name);
Console.WriteLine(string.Join(",", methods));
```

## 常见错误与实践建议

常见错误有三类：忘记 DeclaredOnly，把 ToString、GetHashCode 等继承成员也统计进去；把属性访问器当普通方法重复计数；用 `Type.GetType("短名")` 去找自己程序集里的类型却拿到 null——它只搜索少数核心库，应改用程序集对象或 `GetTypes()` 过滤。反射比直接调用慢，且绕过了编译期检查，普通业务代码应优先用接口与泛型。保持边界意识：反射用于理解元数据，不要用它触碰别人的内部实现或环境信息。

技术核对（2026-10-21）：[Microsoft Learn：reflection](https://learn.microsoft.com/en-us/dotnet/fundamentals/reflection/reflection)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
