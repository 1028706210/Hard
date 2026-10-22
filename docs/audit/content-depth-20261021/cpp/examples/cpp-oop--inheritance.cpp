#include <iostream>
struct Employee {
    virtual ~Employee() = default;
    int level() const { return 1; }
    virtual int salary() const { return 100; }
};
struct Manager : Employee {
    int level() const { return 2; }
    int salary() const override { return 150; }
};
int main() {
    Manager manager;
    Employee& employee = manager;
    std::cout << manager.level() << ' ' << employee.level() << ' '
              << employee.salary() << '\n';
}
