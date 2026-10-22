import java.util.HashSet;
import java.util.Set;
public class Main {
    public static void main(String[] args) {
        Set<String> values = new HashSet<>();
        values.add(null);
        values.add("Ada");
        System.out.println(values.contains(null));
        System.out.println(values.contains("ada"));
        System.out.println(values.contains("Ada"));
    }
}
