class Counter {
    int value;
    static int created;
    Counter() { created++; }
    Counter(int value) { this.value = value; created++; }
}
public class Main {
    public static void main(String[] args) {
        Counter empty = new Counter();
        Counter counter = new Counter(5);
        int value = 6;
        System.out.println(empty.value);
        System.out.println(value);
        System.out.println(counter.value);
        System.out.println(Counter.created);
    }
}
