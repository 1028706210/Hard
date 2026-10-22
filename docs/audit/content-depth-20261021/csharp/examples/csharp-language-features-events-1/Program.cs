using System;
using System.Collections.Generic;
using System.Linq;
var monitor = new TemperatureMonitor(30);
EventHandler<AlertArgs> handler = (_, args) => Console.WriteLine(args.Value);
monitor.Alert += handler;
monitor.Observe(31); // 31
monitor.Alert -= handler;
monitor.Observe(40); // 无输出，已经退订
sealed class AlertArgs : EventArgs
{
    public int Value { get; init; }
}

sealed class TemperatureMonitor
{
    private readonly int _threshold;

    public TemperatureMonitor(int threshold) => _threshold = threshold;

    public event EventHandler<AlertArgs>? Alert;

    public void Observe(int value)
    {
        if (value >= _threshold)
        {
            Alert?.Invoke(this, new AlertArgs { Value = value });
        }
    }
}
