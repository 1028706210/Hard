using System;
using System.Collections.Generic;
using System.Linq;
var report = new Report();
IPrintable view = report;
Console.WriteLine(view.Print()); // report
// report.Print();               // 编译失败：只能通过接口访问

interface IPrintable
{
    string Print();
}

sealed class Report : IPrintable
{
    string IPrintable.Print() => "report";
}

