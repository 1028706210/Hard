import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List<Integer> values = new ArrayList<>(List.of(1, 2, 3, 4));
        Iterator<Integer> iterator = values.iterator();
        while (iterator.hasNext()) {
            if (iterator.next() % 2 == 0) iterator.remove();
        }
        System.out.println(values);
    }
}
