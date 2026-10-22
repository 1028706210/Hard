import java.util.ArrayList;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List<String> values = new ArrayList<>(10);
        System.out.println(values.size());
        values.add("a");
        values.add("b");
        values.add(1, "c");
        System.out.println(values);
        System.out.println(values.set(1, "d"));
    }
}
