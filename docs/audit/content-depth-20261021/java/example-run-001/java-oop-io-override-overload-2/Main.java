public class Main {
    static String choose(long value) { return "long"; }
    static String choose(Integer value) { return "integer"; }
    public static void main(String[] args) {
        System.out.println(choose(1));
        System.out.println(choose(Integer.valueOf(1)));
    }
}
