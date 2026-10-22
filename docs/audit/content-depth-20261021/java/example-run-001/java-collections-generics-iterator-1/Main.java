import java.util.Iterator;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        Iterator<Integer> iterator = List.of(1, 2, 3).iterator();
        int total = 0;
        while (iterator.hasNext()) {
            int value = iterator.next();
            total += value;
        }
        System.out.println(total);
        System.out.println(iterator.hasNext());
    }
}
