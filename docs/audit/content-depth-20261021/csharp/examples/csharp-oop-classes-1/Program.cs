using System;
using System.Collections.Generic;
using System.Linq;
var first = new CounterBox();
var second = first;
second.Value = 7;
Reset(second);
Console.WriteLine(first.Value);                    // 8
Console.WriteLine(ReferenceEquals(first, second)); // True

static void Reset(CounterBox box)
{
    box.Value++;             // 修改双方共享的对象
    box = new CounterBox();  // 仅替换参数中的引用副本
}

sealed class CounterBox
{
    public int Value;
}

