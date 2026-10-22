public class Main {
    static void showLength(Object value) {
        if (value instanceof String text) {
            System.out.println(text.length());
        } else {
            System.out.println("not text");
        }
    }
    public static void main(String[] args) {
        showLength("hello");
        showLength(3);
        showLength(null);
    }
}
