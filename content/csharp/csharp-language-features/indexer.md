---
id: csharp-language-features-indexer
title: 索引器（Indexer）
concepts: [indexer, classes]
objectives:
  - 用 this[int] 语法为类实现索引器，让对象像数组一样按位置存取内部数据。
  - 在索引器中定义明确的越界行为（抛异常或返回约定值），保证调用方对边界输入有可预期的结果。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-indexer.html
source_snapshot_date: 2026-08-23
---

# 索引器（Indexer）

## 概念定义与适用场景

索引器是"带参数的属性"：属性用名字访问，索引器用下标访问，声明关键字是 `this`。当你包装的数据天然有位置含义——通讯录的第 i 个联系人、棋盘的第 r 行第 c 格——索引器能让 `book[i]` 这样的调用读起来像直接操作数组，而内部仍保留完整的存取控制权。

```csharp
sealed class PhoneBook
{
    private readonly string[] _names;

    public PhoneBook(string[] names)
    {
        _names = new string[names.Length];
        Array.Copy(names, _names, names.Length);
    }

    public int Count => _names.Length;

    public string this[int index] =>
        index >= 0 && index < Count ? _names[index] : throw new IndexOutOfRangeException();
}
```

## 语法、API 与边界

索引器的声明形式是 `public string this[int index] { get { ... } set { ... } }`，与属性一样只有 get 时为只读；参数可以不止一个，例如二维索引器 `this[int row, int column]`。索引器重载按参数类型区分：同一个类可以同时有 `this[int]` 与 `this[string]`，分别按序号和按名字取值。越界行为必须自己决定——要么抛出 `IndexOutOfRangeException`（贴近数组语义），要么返回约定值（例如空串），关键是把它写成明确契约，而不是依赖默认行为。构造时复制传入数组，能防止外部改了原数组导致内部状态悄悄变化。

```csharp
var book = new PhoneBook(new[] { "alpha", "beta" });
Console.WriteLine(book[0]);
try
{
    Console.WriteLine(book[5]);
}
catch (IndexOutOfRangeException)
{
    Console.WriteLine("out-of-range");
}
```

### 带参数访问与二维读写

索引器参数不限定为整数，`this[string key]` 可以按名称查数据，多个参数可以表达网格坐标。下例是独立的二维读写示例；其存储与边界来自内部二维数组，写入值通过 set 的 `value` 接收。

```csharp
var grid = new Grid();
grid[1, 0] = 7;
Console.WriteLine(grid[1, 0]); // 7
Console.WriteLine(grid[0, 0]); // 0，数组默认值

sealed class Grid
{
    private readonly int[,] _cells = new int[2, 2];
    public int this[int row, int column]
    {
        get => _cells[row, column];
        set => _cells[row, column] = value;
    }
}
```

这里有效行列都是 0 或 1，`grid[2, 0]` 抛出 IndexOutOfRangeException。普通自定义集合也可以显式抛 ArgumentOutOfRangeException，关键是事先说明合同。返回空串表示缺键时可能与“实际存储空串”混淆，需要无歧义地表达缺失时，可另提供 TryGet 方法。

索引器没有自动实现形式，必须提供访问器实现；它本身也不保证线程安全或快速查找。PhoneBook 复制输入数组可隔离外部数组槽位的修改；若元素是可变对象，浅复制仍然共享对象。当前练习只要求一维只读电话簿与约定的越界处理；二维读写、字符串键和可变元素所有权未被该题验证。

## 常见错误与实践建议

常见错误有三类：在索引器里直接暴露内部数组引用，外部拿到引用就能绕过一切检查，应当返回副本或只读包装；越界行为写得含糊，有的路径返回 null、有的路径抛异常，调用方无法写对 catch；把昂贵的查找逻辑放进 get，却当成廉价下标反复调用。还要区分索引器与普通方法的定位——语法上更简洁，但语义上应表达"按位置/键取数据"。本课练习要求实现电话簿索引器并处理合法与越界两类查询，把边界契约练成肌肉记忆。

技术核对（2026-10-21）：[Microsoft Learn：indexers](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/indexers/)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
