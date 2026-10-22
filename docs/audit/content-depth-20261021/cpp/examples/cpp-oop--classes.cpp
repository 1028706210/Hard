#include <iostream>
#include <stdexcept>
class Score {
    int value_;
public:
    explicit Score(int value) : value_(value) {
        if (value < 0 || value > 100) throw std::invalid_argument("invalid score");
    }
    void add(int delta) {
        if (delta < 0 || delta > 100 - value_) throw std::invalid_argument("invalid delta");
        value_ += delta;
    }
    int value() const { return value_; }
};
int main() {
    Score first(20);
    first.add(5);
    const Score copy = first;
    std::cout << first.value() << ' ' << copy.value() << '\n';
}
