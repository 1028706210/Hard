class Box<T> {
    private final T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
}
public class Main {
    static <T extends Comparable<? super T>> T max(T a, T b) {
        return a.compareTo(b) >= 0 ? a : b;
    }
    public static void main(String[] args) {
        Box<String> name = new Box<>("Ada");
        System.out.println(name.get());
        System.out.println(max(3, 7));
    }
}
