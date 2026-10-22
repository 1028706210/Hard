#include <algorithm>
#include <concepts>
#include <iostream>
#include <ranges>
#include <vector>

template <typename T>
concept Addable = requires(T a, T b) { a + b; };

static_assert(Addable<int>);

int main() {
    std::vector<int> values{5, 3, 1, 4, 2};
    std::ranges::sort(values);
    auto squares = values | std::views::transform([](int v) { return v * v; });
    for (int value : squares) {
        std::cout << value << ' ';
    }
    std::cout << '\n';
    return 0;
}
