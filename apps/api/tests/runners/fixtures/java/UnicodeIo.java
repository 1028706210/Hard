public class UnicodeIo {
    public static void main(String[] args) throws Exception {
        byte[] all = System.in.readAllBytes();
        String name = new String(all, java.nio.charset.StandardCharsets.UTF_8).strip();
        System.out.println("你好，" + name + "！");
    }
}
