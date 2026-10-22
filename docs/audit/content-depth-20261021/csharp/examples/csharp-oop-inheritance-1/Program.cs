using System;
using System.Collections.Generic;
using System.Linq;
var item = new NamedItem("pen"); // 依次输出 base:pen、derived

class Item
{
    protected string Name { get; }
    public Item(string name)
    {
        Name = name;
        Console.WriteLine("base:" + name);
    }
}

sealed class NamedItem : Item
{
    public NamedItem(string name) : base(name) => Console.WriteLine("derived");
}

