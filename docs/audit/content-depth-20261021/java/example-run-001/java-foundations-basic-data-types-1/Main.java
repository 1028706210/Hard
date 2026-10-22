public class Main {
    public static void main(String[] args) {
        long wide = 2147483648L;
        int narrowed = (int) wide;
        int precise = 16777217;
        float rounded = precise;
        System.out.println(wide);
        System.out.println(narrowed);
        System.out.println((int) rounded);
        System.out.println((int) 3.9);
    }
}
