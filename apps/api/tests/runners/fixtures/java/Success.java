import java.nio.charset.StandardCharsets;

public class Success {
    public static void main(String[] args) throws Exception {
        byte[] all = System.in.readAllBytes();
        String name = new String(all, StandardCharsets.UTF_8).strip();
        System.out.println("Hello, " + name + "!");
    }
}
