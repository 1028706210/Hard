class Base {
    Base() { System.out.println("base"); }
}
class Child extends Base {
    int value = initialValue();
    private static int initialValue() {
        System.out.println("field");
        return 1;
    }
    Child() { super(); System.out.println("body"); }
}
public class Main {
    public static void main(String[] args) { new Child(); }
}
