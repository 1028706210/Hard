class Counter { int value; }
public class Main {
    public static void main(String[] args) {
        Counter original = new Counter();
        Counter alias = original;
        alias.value = 7;
        System.out.println(original.value);
        original = null;
        System.out.println(alias.value);
    }
}
