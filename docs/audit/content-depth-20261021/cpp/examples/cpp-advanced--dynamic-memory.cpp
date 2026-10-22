#include <iostream>
#include <memory>
#include <utility>
int main() {
    auto owner = std::make_unique<int>(7);
    int* observer = owner.get();
    auto next_owner = std::move(owner);
    std::cout << (owner == nullptr) << ' ' << *next_owner << ' '
              << *observer << '\n';
}
