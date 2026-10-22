using System;
using System.Collections.Generic;
using System.Linq;
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

