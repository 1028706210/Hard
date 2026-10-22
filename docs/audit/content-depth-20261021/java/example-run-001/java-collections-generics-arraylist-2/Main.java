import java.util.ArrayList;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List<Integer> values = new ArrayList<>(List.of(3, 1, 2, 1));
        System.out.println(values.remove(1));
        System.out.println(values.remove(Integer.valueOf(1)));
        System.out.println(values);
    }
}
