class Resource implements AutoCloseable {
    private final String name;
    Resource(String name) { this.name = name; }
    public void close() { System.out.println("close:" + name); }
}
public class Main {
    public static void main(String[] args) {
        try (Resource first = new Resource("A");
             Resource second = new Resource("B")) {
            System.out.println("work");
            throw new IllegalStateException("failed");
        } catch (IllegalStateException error) {
            System.out.println("caught:" + error.getMessage());
        }
    }
}
