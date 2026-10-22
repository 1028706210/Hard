#include <iostream>
void increase(int* value) {
    if (value != nullptr) ++*value;
}
int main() {
    int first = 4, second = 9;
    const int* read_only = &first;
    read_only = &second;  // 可以改指向，不能通过它改对象
    int* const fixed = &first;
    *fixed = 6;          // 可以改对象，不能改 fixed 的指向
    increase(fixed);
    increase(nullptr);
    std::cout << first << ' ' << *read_only << '\n';
}
