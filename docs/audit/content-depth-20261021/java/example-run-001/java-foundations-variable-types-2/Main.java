import java.util.Arrays;
public class Main {
    public static void main(String[] args) {
        final int[] values = {1, 2};
        values[0] = 9;
        var size = values.length;
        System.out.println(Arrays.toString(values));
        System.out.println(size);
    }
}
