import java.util.Objects;
public class Main {
    public static void main(String[] args) {
        String first = new String("Ada");
        String second = new String("Ada");
        System.out.println(first == second);
        System.out.println(first.equals(second));
        System.out.println(Objects.equals(null, null));
        System.out.println(first.getClass().getName());
    }
}
