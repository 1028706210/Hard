---
id: csharp-oop-nullable
title: 可空类型
concepts: [nullable-types, types]
objectives:
  - 用 int? 与 HasValue、GetValueOrDefault 表达可能缺失的值。
  - 区分可空值类型（Nullable&lt;T&gt;）与可空引用类型（string?）。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-nullable.html
source_snapshot_date: 2026-08-23
---

# 可空类型

## 概念定义与适用场景

值类型默认没有"不存在"这个状态，`int?`（即 `Nullable<int>`）在 int 之外增加了 null，用来表示"这次没有值"。读取用户输入、查询可能无结果的数据时，可空类型能把缺失显式写进类型系统。

```csharp
int? quantity = null;
if (quantity.HasValue) Console.WriteLine(quantity.Value);
else Console.WriteLine("none");
```

## 语法、API 与边界

可空引用类型 `string?` 与 `int?` 机制不同：`string?` 不改变运行时行为，而是告诉编译器该引用可能为 null，需要先判空再解引用。`??` 与 `??=` 运算符可以在值为 null 时提供回退值。

```csharp
var name = Console.ReadLine() ?? "learner";
int? parsed = int.TryParse(name, out var value) ? value : null;
Console.WriteLine(parsed.GetValueOrDefault());
```

### 缺失、零与空字符串是不同状态

`int?` 默认值是 null；`int` 默认值是 0。`GetValueOrDefault()` 返回底层类型默认值，所以会把缺失与真实的 0 合并；如果业务需要区分二者，必须先用 `HasValue` 或模式匹配保留这个区别。`??` 只对 null 回退，不会替换空字符串。

```csharp
int? missing = null;
int? zero = 0;
Console.WriteLine(missing ?? -1); // -1
Console.WriteLine(zero ?? -1);    // 0
Console.WriteLine((missing + 2) is null); // True，可空算术传播 null
Console.WriteLine(missing < zero);       // False，不能据此认定 missing >= zero
string? empty = "";
Console.WriteLine((empty ?? "fallback").Length); // 0
```

对可空数值做 `<`、`>` 等关系比较时，只要有一边缺失，结果为 false；相等比较规则不同，两个 null 相等。不要把缺失数据排序、计算的业务规则偷偷交给这些默认行为。

```csharp
#nullable enable
string? name = null;
Console.WriteLine(name?.Length ?? -1); // -1，不会解引用 null
name ??= "Li";
Console.WriteLine(name.Length);        // 2
```

可空引用分析需要在项目或文件中启用；它给出编译诊断，不能阻止外部代码在运行期传入 null。`name!` 只是抑制警告，不会插入校验或创建对象。对不可信边界仍要检查 null。这里的 `?.` 表达式只在接收者非 null 时访问成员，后面的 `??` 再给出缺失时的结果。

本课练习区分空输入、解析失败及合法值；它没有验证全部提升运算规则或可空编译诊断，代码示例不能替代这些额外检查。

## 常见错误与实践建议

对值为 null 的 `int?` 直接访问 `.Value` 会抛出 InvalidOperationException，访问前应检查 HasValue 或改用 GetValueOrDefault。不要把"空字符串"和 null 混为一谈：空字符串仍然是有效的引用。本课练习把空输入、非数字输入当作不同分支分别处理。

技术核对（2026-10-21）：[Microsoft Learn：nullable-value-types](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/nullable-value-types)；[Microsoft Learn：nullable-references](https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
