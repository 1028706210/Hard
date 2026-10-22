class Learner {
    private final String name;
    private static int count;
    Learner(String name) { this.name = name; count++; }
    String greet() { return "Hello, " + name; }
    static int count() { return count; }
}
public class Main {
    public static void main(String[] args) {
        Learner first = new Learner("Ada");
        Learner second = new Learner("Lin");
        System.out.println(first.greet());
        System.out.println(second.greet());
        System.out.println(Learner.count());
    }
}
