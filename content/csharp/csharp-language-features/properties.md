---
id: csharp-language-features-properties
title: 属性（Property）
concepts: [properties, encapsulation]
objectives:
  - 使用自动实现的属性与 private set 受控属性封装对象状态，并在访问器中加入校验规则。
  - 说明属性与公共字段的区别：属性是访问器方法对，能在不改变调用方写法的前提下加入校验与计算逻辑。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-property.html
source_snapshot_date: 2026-08-23
---

# 属性（Property）

## 概念定义与适用场景

属性给对象状态提供一扇受控的门：调用方写作 `account.Balance`，看起来像读字段，实际执行的是 get 访问器方法。正因为读写都是方法，校验、派生计算、通知等逻辑可以藏在访问器里，外部毫无感知。余额不允许随意改、年龄不允许为负，这类约束都应该由属性把守，而不是靠调用方自觉。

```csharp
sealed class Account
{
    public string Id { get; }
    public int Balance { get; private set; }

    public Account(string id, int initialBalance)
    {
        Id = id;
        Balance = initialBalance;
    }

    public void Deposit(int amount)
    {
        if (amount > 0) Balance += amount;
    }
}
```

## 语法、API 与边界

`public int Count { get; set; }` 是自动实现的属性：编译器生成一个隐藏后备字段和 `get_Count`/`set_Count` 两个访问器方法。`{ get; private set; }` 表示任何代码都能读、只有类内部能写，这是"只读对外、可变对内"的标准写法。get 或 set 也可以只保留一个，省略 set 的属性只能读。完整形式的属性手写后备字段，例如 `public int Level { get { return _level; } private set { _level = Math.Max(0, value); } }`，把规则集中在一处。

```csharp
sealed class Battery
{
    private int _level;

    public int Level
    {
        get => _level;
        private set => _level = Math.Clamp(value, 0, 100);
    }

    public void Charge(int delta) => Level += delta;
}
```

### get、private set 与 init 的边界

只有 get 的自动属性可以在声明它的类型的构造函数中初始化；private set 允许该类型在后续方法中继续赋值；init 允许在构造阶段、对象初始化器等初始化上下文中赋值，此后普通赋值会编译失败。只读属性返回可变列表时，列表仍可能被修改，不能把“无法重新赋值属性”当作深度不可变。

```csharp
var badge = new Badge { Name = "Lin" };
Console.WriteLine(badge.Caption); // Hello, Lin
// badge.Name = "Chen";            // 编译失败：初始化后不可再写 init 属性

sealed class Badge
{
    public string Name { get; init; } = "guest";
    public string Caption => "Hello, " + Name;
}
```

计算属性不必存储后备字段；`Caption` 每次读取都会计算。完整 set 中的隐式参数 `value` 是本次写入值。若写成 `set => Age = value;`，访问器会递归调用自己直到栈耗尽，正确目标应是后备字段。规则可以选择拒绝负数或钳制到边界，但必须与公开合同一致，不能悄悄混用。

属性可以同时有 get/set、只有 get，或仅有 set；表达式体 get 也不等于自动属性。示例 Account 的构造赋值只演示语法，实际余额模型还需拒绝非法初始值并考虑金额溢出。本课账户练习的输入边界与预期输出由题目约定，此处没有更改它们。字段改为属性通常保留源代码调用形式，但不是二进制兼容保证：对外发布的库仍需重新评估使用方。

## 常见错误与实践建议

公开字段允许调用方直接写入未经验证的状态；属性则能把写入规则集中在访问器中。把字段换为属性通常可以保留源代码访问形式，但已编译使用方仍需考虑兼容性。第二类错误是把重活塞进 get 访问器——每次读取都触发数据库查询或排序，调用方完全察觉不到；get 应当廉价、可重复。还有一点：属性访问器会生成方法，反射统计方法时要用 `IsSpecialName` 排除它们。本课练习要求用属性实现带规则的账户操作，体会"规则写在访问器与业务方法里、调用方保持简洁"的分工。

技术核对（2026-10-21）：[Microsoft Learn：properties](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/properties)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
