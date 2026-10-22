abstract class Shape {
    private final String name;
    Shape(String name) { this.name = name; }
    abstract double area();
    final String describe() { return name + ":" + Math.round(area()); }
}
class Circle extends Shape {
    private final double radius;
    Circle(String name, double radius) {
        super(name);
        if (radius < 0) throw new IllegalArgumentException("negative radius");
        this.radius = radius;
    }
    @Override double area() { return Math.PI * radius * radius; }
}
public class Main {
    public static void main(String[] args) {
        Shape shape = new Circle("disk", 2);
        System.out.println(shape.describe());
    }
}
