#include <iostream>
struct Reader {
    virtual ~Reader() = default;
    virtual int read() = 0;
};
struct FixedReader : Reader {
    int read() override { return 6; }
};
int twice(Reader& reader) { return reader.read() + reader.read(); }
int main() {
    FixedReader reader;
    std::cout << twice(reader) << '\n';
}
