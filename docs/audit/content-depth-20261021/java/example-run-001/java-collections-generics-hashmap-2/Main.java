import java.util.HashMap;
import java.util.Map;
public class Main {
    public static void main(String[] args) {
        Map<String, Integer> counts = new HashMap<>();
        for (String word : new String[]{"a", "b", "a"}) {
            counts.put(word, counts.getOrDefault(word, 0) + 1);
        }
        System.out.println(counts.get("a"));
        System.out.println(counts.get("b"));
        System.out.println(counts.size());
    }
}
