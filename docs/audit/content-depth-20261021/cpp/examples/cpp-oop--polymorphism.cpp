#include <iostream>
#include <memory>
struct Instrument {
    virtual ~Instrument() = default;
    virtual int notes() const { return 1; }
};
struct Piano : Instrument {
    int notes() const override { return 88; }
};
int main() {
    Piano piano;
    const Instrument& view = piano;
    Instrument sliced = piano;
    std::unique_ptr<Instrument> owner = std::make_unique<Piano>();
    std::cout << view.notes() << ' ' << sliced.notes() << ' '
              << owner->notes() << '\n';
}
