using System;
using System.Collections.Generic;
using System.Linq;
Transformer operations = TransformOps.Square;
operations += TransformOps.Negate;
Console.WriteLine(operations(4)); // -4：最后一个处理器返回值
var piped = 4;
foreach (Transformer operation in operations.GetInvocationList())
    piped = operation(piped);
Console.WriteLine(piped);        // -16：手工传递中间结果
delegate int Transformer(int x);

static class TransformOps
{
    public static int Square(int x) => x * x;
    public static int Negate(int x) => -x;
}
