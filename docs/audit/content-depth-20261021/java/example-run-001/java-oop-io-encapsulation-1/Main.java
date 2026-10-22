class Account {
    private int balance;
    boolean deposit(int amount) {
        if (amount <= 0) return false;
        balance = Math.addExact(balance, amount);
        return true;
    }
    int getBalance() { return balance; }
}
public class Main {
    public static void main(String[] args) {
        Account account = new Account();
        System.out.println(account.deposit(100));
        System.out.println(account.deposit(-5));
        System.out.println(account.getBalance());
    }
}
