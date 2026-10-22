public class Main {
    public static void main(String[] args) {
        int a = 50_000;
        long tooLate = a * a;
        long correct = (long) a * a;
        System.out.println(tooLate);
        System.out.println(correct);
        System.out.println(5 / 2);
        System.out.println(5 / 2.0);
    }
}
