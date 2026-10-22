using System;
using System.Collections.Generic;
using System.Linq;
Animal animal = new Cat();
Console.WriteLine(animal.Speak());       // meow
Console.WriteLine(animal.Label());       // animal
Console.WriteLine(((Cat)animal).Label()); // cat

class Animal
{
    public virtual string Speak() => "sound";
    public string Label() => "animal";
}

class Cat : Animal
{
    public override string Speak() => "meow";
    public new string Label() => "cat";
}

