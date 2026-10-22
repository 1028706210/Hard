#include <iostream>
#include <string>
template<class T>
class Box {
    T value_;
public:
    explicit Box(const T& value) : value_(value) {}
    const T& get() const { return value_; }
};
template<class T>
T larger(T first, T second) { return first < second ? second : first; }
int main() {
    Box<std::string> label("orbit");
    std::cout << larger(3, 7) << ' ' << larger<double>(3, 2.5)
              << ' ' << label.get() << '\n';
}
