import java.util.LinkedList;
public class Main {
    public static void main(String[] args) {
        LinkedList<Integer> values = new LinkedList<>();
        for (int value : new int[]{1, 2, 3}) values.addFirst(value);
        System.out.println(values);
        System.out.println(values.peekFirst());
        System.out.println(values.peekLast());
    }
}
