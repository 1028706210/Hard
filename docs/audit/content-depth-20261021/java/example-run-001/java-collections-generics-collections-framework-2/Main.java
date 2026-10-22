import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List<String> source = new ArrayList<>(List.of("a"));
        List<String> snapshot = List.copyOf(source);
        List<String> view = Collections.unmodifiableList(source);
        source.add("b");
        System.out.println(snapshot);
        System.out.println(view);
    }
}
