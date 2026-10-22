using System;
using System.Collections.Generic;
using System.Linq;
var first = new Snapshot { Count = 1, Items = new List<int> { 10 } };
var second = first;
second.Count = 2;
second.Items.Add(20);
Console.WriteLine(first.Count);       // 1
Console.WriteLine(first.Items.Count); // 2

struct Snapshot
{
    public int Count;
    public List<int> Items;
}

