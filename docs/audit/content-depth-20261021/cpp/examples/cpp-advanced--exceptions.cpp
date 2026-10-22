#include <iostream>
#include <stdexcept>
#include <string>
int parse_all(const std::string& text) {
    std::size_t used = 0;
    int value = std::stoi(text, &used);
    if (used != text.size()) throw std::invalid_argument("trailing input");
    return value;
}
int main() {
    for (const std::string text : {"42", "42x", "99999999999999999999"}) {
        try {
            const int value = parse_all(text);
            std::cout << value << '\n';
        } catch (const std::invalid_argument&) {
            std::cout << "invalid\n";
        } catch (const std::out_of_range&) {
            std::cout << "range\n";
        }
    }
}
