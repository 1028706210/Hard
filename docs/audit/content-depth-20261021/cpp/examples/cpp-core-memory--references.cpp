#include <iostream>
#include <string>
void append_mark(std::string& text) { text += '!'; }
std::size_t length(const std::string& text) { return text.size(); }
int main() {
    int first = 3, second = 8;
    int& alias = first;
    alias = second;
    second = 10;
    std::string message = "hi";
    append_mark(message);
    std::cout << first << ' ' << second << ' ' << length(message) << '\n';
}
