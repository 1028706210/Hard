---
id: csharp-oop-namespaces
title: 命名空间
concepts: [namespaces, types]
objectives:
  - 用 namespace 组织类型并用全限定名区分同名类型。
  - 解析全限定名，区分命名空间部分与类型短名。
prerequisites: [csharp-oop-classes]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-namespace.html
source_snapshot_date: 2026-08-23
---

# 命名空间

## 概念定义与适用场景

namespace 把类型组织成层次结构，避免大型项目中同名类型冲突。`Hard.Core.Util` 这样的全限定名精确指出类型所在位置，即使项目里还有另一个 `Util` 也不会混淆。

```csharp
namespace Hard.Core
{
    class Util
    {
        public static string Tag() => "core";
    }
}
```

## 语法、API 与边界

`using Hard.Core;` 指令引入该命名空间的成员，使代码可以按短名 `Util` 使用。全限定名用点分段，每一段都不能为空；没有命名空间的类型属于全局命名空间。文件范围的 `namespace Hard.Core;` 写法（末尾分号）可以让整个文件只缩进一次。

```csharp
var qualified = "Hard.Core.Util";
var lastDot = qualified.LastIndexOf('.');
Console.WriteLine(qualified[..lastDot]);
Console.WriteLine(qualified[(lastDot + 1)..]);
```

## 常见错误与实践建议

命名空间影响的是类型的组织与查找，不会改变运行性能，也不等于程序集。手写全限定名解析时注意边界：`A..B` 这种空段是非法的，首段为空同样非法。本课练习把"最后一个点"之前当作命名空间、之后当作短名，并明确处理无点与空段的分支。
