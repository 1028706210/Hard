import java.util.ArrayList;
import java.util.List;
class Scores {
    private final List<Integer> values;
    Scores(List<Integer> values) { this.values = new ArrayList<>(values); }
    List<Integer> snapshot() { return List.copyOf(values); }
}
public class Main {
    public static void main(String[] args) {
        List<Integer> original = new ArrayList<>(List.of(90));
        Scores scores = new Scores(original);
        original.clear();
        System.out.println(scores.snapshot().size());
    }
}
