interface Printable {
    String text();
    default String print() { return format(text()); }
    private String format(String value) { return "Hello, " + value; }
    static int version() { return 2; }
}
class Label implements Printable {
    public String text() { return "Ada"; }
}
public class Main {
    public static void main(String[] args) {
        System.out.println(new Label().print());
        System.out.println(Printable.version());
    }
}
