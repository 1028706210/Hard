import java.util.HashMap;
import java.util.Map;
public class Main {
    public static void main(String[] args) {
        Map<String, Integer> scores = new HashMap<>();
        System.out.println(scores.put("Ada", 10));
        System.out.println(scores.put("Ada", 20));
        System.out.println(scores.get("Ada"));
        System.out.println(scores.size());
    }
}
