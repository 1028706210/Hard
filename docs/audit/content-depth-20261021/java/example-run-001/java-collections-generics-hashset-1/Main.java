import java.util.HashSet;
import java.util.Set;
public class Main {
    public static void main(String[] args) {
        Set<String> values = new HashSet<>();
        System.out.println(values.add("a"));
        System.out.println(values.add("a"));
        values.add("b");
        System.out.println(values.remove("b"));
        System.out.println(values.size());
    }
}
