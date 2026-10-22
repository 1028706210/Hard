import java.util.HashSet;
import java.util.Set;
final class User {
    private final int id;
    User(int id) { this.id = id; }
    @Override public boolean equals(Object other) {
        if (this == other) return true;
        if (!(other instanceof User user)) return false;
        return id == user.id;
    }
    @Override public int hashCode() { return Integer.hashCode(id); }
    @Override public String toString() { return "User:" + id; }
}
public class Main {
    public static void main(String[] args) {
        User first = new User(7);
        User second = new User(7);
        Set<User> users = new HashSet<>();
        users.add(first);
        users.add(second);
        System.out.println(first.equals(second));
        System.out.println(users.size());
        System.out.println(first);
    }
}
