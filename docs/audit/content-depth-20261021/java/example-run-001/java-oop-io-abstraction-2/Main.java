interface Vocal { String sound(); }
abstract class Animal implements Vocal {
    void greet() { System.out.println(sound() + "!"); }
}
class Cat extends Animal {
    public String sound() { return "Meow"; }
}
public class Main {
    public static void main(String[] args) { new Cat().greet(); }
}
