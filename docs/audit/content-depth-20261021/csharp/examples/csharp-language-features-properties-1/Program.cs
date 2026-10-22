using System;
using System.Collections.Generic;
using System.Linq;
var badge = new Badge { Name = "Lin" };
Console.WriteLine(badge.Caption); // Hello, Lin
// badge.Name = "Chen";            // 编译失败：初始化后不可再写 init 属性

sealed class Badge
{
    public string Name { get; init; } = "guest";
    public string Caption => "Hello, " + Name;
}

