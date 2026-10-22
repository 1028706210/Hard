---
id: csharp-io-metadata-attributes
title: 特性（Attribute）
concepts: [attributes, classes]
objectives:
  - 定义带 AttributeUsage 限制与属性参数的自定义特性，并把它应用到类上。
  - 运行期通过 GetCustomAttribute 读取特性元数据，说明特性数据保存在程序集元数据中、本身不产生行为。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-attribute.html
source_snapshot_date: 2026-08-23
---

# 特性（Attribute）

## 概念定义与适用场景

特性是一种把声明式元数据附着到类型、方法等程序元素上的机制。特性本身不执行任何逻辑，它只是被写进程序集元数据的一块数据；真正使用这些数据的是运行期的反射代码。给任务类标注负责人和优先级、给导出方法标注版本号，都是典型用法。

```csharp
[AttributeUsage(AttributeTargets.Class)]
sealed class TaskInfoAttribute : Attribute
{
    public string Owner { get; init; } = "";
    public int Priority { get; init; }
}

[TaskInfo(Owner = "ops", Priority = 2)]
sealed class Audit { }
```

## 语法、API 与边界

自定义特性必须直接或间接继承 `System.Attribute`；`AttributeUsage` 限定它能贴在哪些目标上（类、方法、返回值等），默认可以重复贴用同一目标多次吗？——默认不可以，`AllowMultiple = true` 才允许。方括号里的 `Owner = "ops"` 不是命名参数语法糖给构造函数，而是给特性的属性赋值。读取用 `Attribute.GetCustomAttribute(type, typeof(...))` 或泛型版 `type.GetCustomAttribute<T>()`，找不到时返回 null。

```csharp
using System.Reflection;

var info = typeof(Audit).GetCustomAttribute<TaskInfoAttribute>();
if (info is not null)
{
    Console.WriteLine($"{info.Owner} {info.Priority}");
}
```

## 常见错误与实践建议

初学者常以为给方法贴上特性就会自动执行某些逻辑——不会，特性只是数据，必须有代码去读取它（通常是反射或框架的基础设施）。第二类错误是忘了 `AttributeUsage`，导致特性被贴到不合适的目标上，问题在运行期才暴露。特性属性的书写形式像命名参数，但它要求属性可写（或为字段），且类型限于常量、Type、枚举及其一维数组。本课练习要求自定义特性并经反射读出元数据，让"声明"与"读取"两侧都得到训练。
