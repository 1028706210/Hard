class Base {
    String show(Object value) { return "base-object"; }
    String show(String value) { return "base-string"; }
}
class Sub extends Base {
    @Override String show(Object value) { return "sub-object"; }
    @Override String show(String value) { return "sub-string"; }
}
public class Main {
    public static void main(String[] args) {
        Base printer = new Sub();
        Object text = "hi";
        System.out.println(printer.show(text));
        System.out.println(printer.show("hi"));
    }
}
