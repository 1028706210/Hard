interface Shape { double area(); }
class Circle implements Shape {
    private final double radius;
    Circle(double radius) { this.radius = radius; }
    public double area() { return Math.PI * radius * radius; }
    double radius() { return radius; }
}
class Square implements Shape {
    private final double side;
    Square(double side) { this.side = side; }
    public double area() { return side * side; }
}
public class Main {
    public static void main(String[] args) {
        Shape[] shapes = {new Circle(2), new Square(3)};
        for (Shape shape : shapes) System.out.println(Math.round(shape.area()));
    }
}
