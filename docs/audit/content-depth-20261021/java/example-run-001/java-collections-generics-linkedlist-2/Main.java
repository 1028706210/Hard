import java.util.Deque;
import java.util.LinkedList;
public class Main {
    public static void main(String[] args) {
        Deque<String> queue = new LinkedList<>();
        queue.offerLast("a");
        queue.offerLast("b");
        System.out.println(queue.pollFirst());
        System.out.println(queue.pollFirst());
        System.out.println(queue.pollFirst());
    }
}
