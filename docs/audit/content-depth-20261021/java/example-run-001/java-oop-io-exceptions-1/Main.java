public class Main {
    static void parse(String text) {
        try {
            int value = Integer.parseInt(text);
            System.out.println("OK:" + value);
        } catch (NumberFormatException error) {
            System.out.println("ERROR");
        } finally {
            System.out.println("done");
        }
    }
    public static void main(String[] args) {
        parse("12");
        parse("abc");
    }
}
