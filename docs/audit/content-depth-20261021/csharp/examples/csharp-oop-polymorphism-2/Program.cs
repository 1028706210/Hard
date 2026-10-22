using System;
using System.Collections.Generic;
using System.Linq;
Figure figure = new UnitSquare();
Console.WriteLine(figure.Area()); // 1

abstract class Figure
{
    public abstract int Area();
    public string Unit => "square-unit";
}

sealed class UnitSquare : Figure
{
    public override int Area() => 1;
}

