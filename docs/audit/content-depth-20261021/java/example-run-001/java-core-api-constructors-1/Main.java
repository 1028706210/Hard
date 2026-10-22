class Person {
    private final String name;
    private final int age;
    Person() { this("guest", 0); }
    Person(String name, int age) {
        if (name == null || name.isBlank() || age < 0) {
            throw new IllegalArgumentException("invalid person");
        }
        this.name = name;
        this.age = age;
    }
    String describe() { return name + ":" + age; }
}
public class Main {
    public static void main(String[] args) {
        System.out.println(new Person().describe());
        System.out.println(new Person("Ada", 18).describe());
    }
}
