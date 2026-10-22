using System;
using System.Collections.Generic;
using System.Linq;
int value = 3;
object boxed = value;
value = 9;
Console.WriteLine((int)boxed); // 3，拆箱类型必须与箱中实际类型匹配

