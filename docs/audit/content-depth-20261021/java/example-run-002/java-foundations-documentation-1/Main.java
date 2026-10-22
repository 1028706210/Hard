/** 展示整数平方方法的公开契约。 */
public class Main {
    /**
     * 返回非负整数的平方。
     * <p>只接受能让结果放入 int 的本例范围。
     * 比较表达式可写为 {@code 0 <= value && value <= 46340}。
     *
     * @param value 范围为 0 到 46340（包含端点）的整数
     * @return value 的平方
     * @throws IllegalArgumentException value 为负数或超过 46340
     */
    public static int square(int value) {
        if (value < 0 || value > 46340) {
            throw new IllegalArgumentException("out of range");
        }
        return value * value;
    }

    /**
     * 运行一个成功调用和一个拒绝调用。
     * @param args 本示例不使用命令行参数
     */
    public static void main(String[] args) {
        System.out.println(square(3));
        try {
            square(-1);
        } catch (IllegalArgumentException error) {
            System.out.println("rejected");
        }
    }
}
