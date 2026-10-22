class Animal {
    private final String name;
    Animal(String name) { this.name = name; }
    String getName() { return name; }
    String speak() { return "..."; }
}
class Dog extends Animal {
    Dog(String name) { super(name); }
    @Override String speak() { return "Woof"; }
    String compare() { return super.speak() + "/" + speak(); }
}
public class Main {
    public static void main(String[] args) {
        Dog dog = new Dog("Rex");
        System.out.println(dog.getName() + ":" + dog.speak());
        System.out.println(dog.compare());
    }
}
