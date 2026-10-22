#include <iostream>
#include <vector>
int main() {
    std::vector<int> values{1, 2, 3, 4, 5};
    for (auto it = values.begin(); it != values.end();) {
        if (*it % 2 == 0) it = values.erase(it);
        else ++it;
    }
    for (int value : values) std::cout << value << ' ';
    std::cout << '\n';
}
