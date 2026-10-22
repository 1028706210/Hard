#include <iostream>
#include <vector>
int main() {
    std::vector<int> values;
    values.reserve(8);
    std::cout << values.size() << ' ' << (values.capacity() >= 8) << '\n';
    values.resize(3, 2);
    values.push_back(5);
    int total = 0;
    for (const int value : values) total += value;
    std::cout << values.size() << ' ' << total << '\n';
}
