interface Calculator { int calc(int a, int b); }
class Add implements Calculator {
    public int calc(int a, int b) { return a + b; }
}
class Subtract implements Calculator {
    public int calc(int a, int b) { return a - b; }
}
public class Main {
    public static void main(String[] args) {
        Calculator[] operations = {new Add(), new Subtract()};
        for (Calculator operation : operations) {
            System.out.println(operation.calc(3, 4));
        }
    }
}
