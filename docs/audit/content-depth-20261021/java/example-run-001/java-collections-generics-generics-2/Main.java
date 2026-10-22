import java.util.ArrayList;
import java.util.List;
public class Main {
    static double sum(List<? extends Number> values) {
        double result = 0;
        for (Number value : values) result += value.doubleValue();
        return result;
    }
    static void addSeven(List<? super Integer> target) { target.add(7); }
    public static void main(String[] args) {
        System.out.println(sum(List.of(1, 2)));
        List<Number> numbers = new ArrayList<>();
        addSeven(numbers);
        System.out.println(numbers);
    }
}
