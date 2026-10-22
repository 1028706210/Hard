class Base {
    String label = "base";
    String describe() { return label; }
}
class Child extends Base {
    String label = "child";
    @Override String describe() { return label; }
}
public class Main {
    public static void main(String[] args) {
        Base reference = new Child();
        System.out.println(reference.label);
        System.out.println(reference.describe());
    }
}
