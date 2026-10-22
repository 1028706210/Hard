import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
public class Main {
    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("c", "a", "b"));
        Collections.sort(names);
        Set<String> unique = new TreeSet<>(List.of("c", "a", "a", "b"));
        System.out.println(names);
        System.out.println(unique);
    }
}
