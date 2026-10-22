#include <cstdlib>

int main(int argc, char** argv) {
    if (argc > 1) {
        volatile int value = 0;
        while (true) {
            value = 0;
        }
    }
    std::system(".\\hard_submission.exe child");
    return 0;
}
