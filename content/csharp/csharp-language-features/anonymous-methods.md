---
id: csharp-language-features-anonymous-methods
title: 匿名方法（Anonymous Method）
concepts: [anonymous-methods, delegates]
objectives:
  - 用 delegate 匿名方法与 lambda 表达式就地定义委托逻辑，说明两者可绑定到同一委托类型的兼容关系。
  - 把匿名委托作为参数传给 List<T>.FindAll / ConvertAll 等泛型 API，完成过滤与变换两步管道。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-anonymous-methods.html
source_snapshot_date: 2026-08-23
---

# 匿名方法（Anonymous Method）

## 概念定义与适用场景

委托逻辑常常只在某一处使用：为它起名字、找位置写一个完整方法，反而打断了阅读流。匿名方法（`delegate (int x) { ... }`）与它的现代写法 lambda（`x => x * x`）允许把方法体就地写在需要委托的地方，"这段判断规则"和"用它过滤"在同一行里一目了然。C# 2.0 先有匿名方法，C# 3.0 的 lambda 是更简洁的匿名函数语法，两者都能绑定到同一个委托类型。

```csharp
Predicate<int> isEven = delegate (int value) { return value % 2 == 0; };
Func<int, int> square = value => value * value;
```

## 语法、API 与边界

匿名方法以 `delegate (参数) { 方法体 }` 形式书写，参数类型必须显式；lambda 用 `参数 => 表达式` 或 `参数 => { 方法体 }`，参数类型通常可以省略，由目标委托类型推断。`List<T>.FindAll(Predicate<T>)` 用判定委托保留元素并返回新列表；`ConvertAll<T>(Converter<T,TResult>)` 用转换委托立即生成映射后的新列表，两步串联就是一条过滤-变换管道。边界：匿名方法里不能有跳出到外层的 break/continue；表达式 lambda 可以转换为表达式树（`Expression<Func<...>>`），但表达式树不能直接像委托一样调用，需要先 Compile 为委托；语句体 lambda 不支持该转换。lambda 虽简洁，但多语句、复杂分支的逻辑用带语句体的形式保持可读。

```csharp
var numbers = new List<int> { 1, 2, 3, 4, 5, 6 };
var evens = numbers.FindAll(delegate (int value) { return value % 2 == 0; });
var squares = evens.ConvertAll(value => value * value);
Console.WriteLine(string.Join(" ", squares));
```

### 闭包捕获变量，不是冻结当时的数值

```csharp
int factor = 2;
Func<int, int> scale = value => value * factor;
factor = 3;
Console.WriteLine(scale(4)); // 12

var actions = new List<Action>();
for (int index = 0; index < 2; index++)
{
    int captured = index; // 每轮独立变量
    actions.Add(() => Console.WriteLine(captured));
}
foreach (var action in actions) action(); // 依次 0、1
```

若 for 循环直接捕获 index，两次延后调用都会读到结束后的 2。现代 foreach 的迭代变量每轮独立，不能把这条 for 的规则原样套用到 foreach。需要无捕获函数时可使用 static lambda，编译器会阻止它捕获外部局部变量。

表达式 lambda 可在合适上下文中转换为表达式树，表达式树描述代码而不是直接作为委托调用；语句体 lambda 则不能转换为表达式树。本章先掌握委托形式即可，不要求引入表达式树基础设施。本课过滤平方练习只验证立即过滤和转换，闭包生命周期与查询表达式树没有纳入题目合同。

## 常见错误与实践建议

初学者常见的错误：混淆 `FindAll`（立即生成新的 List，原列表不变）与 LINQ 的 `Where`（延迟枚举，返回 IEnumerable），把后者的结果当成已物化列表反复遍历；在循环里捕获循环变量又期望它保持当时的值——匿名函数捕获的是变量本身而非值，for 与现代 foreach 对迭代变量的规则不同，见后文对照；用匿名方法实现过长逻辑，缩进层层嵌套，此时命名方法更清晰。参数推断方面，绑定到 `Predicate<T>`、`Converter<T,TResult>` 这类现成泛型委托时优先让编译器推断，避免手写类型噪音。本课练习要求实现"筛偶数、再平方"的管道，模块综合挑战则组合属性、集合、泛型委托与匿名方法完成低库存报告。

技术核对（2026-10-21）：[Microsoft Learn：lambda-expressions](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
