public class BigOutput {
    public static void main(String[] args) {
        StringBuilder builder = new StringBuilder();
        for (int index = 0; index < 9000; index += 1) {
            builder.append("output-overflow-");
        }
        System.out.println(builder);
    }
}
