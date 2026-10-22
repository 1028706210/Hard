"""One-off, guarded C++ lesson depth pass. Does not touch exercise contracts."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[4]
MARKER = "## 深入理解与完整示例"
LESSONS = {
    "cpp-oop/classes": ("""
构造函数负责让对象从一开始就处于有效状态；成员初始化按类中声明顺序进行，不能靠调换初始化列表改变顺序。`explicit` 阻止单参数构造函数参与意外的隐式转换。`const` 成员函数限制通过 `this` 修改普通成员，但不代表它不会修改 `mutable` 成员或外部对象。

下面的计分对象拒绝非法初值、受控地增加分数，并允许在只读对象上查询。

```cpp
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
    std::cout << first.value() << ' ' << copy.value() << '\\n';
}
```

输出为 `25 25`。按值复制得到独立对象；这与 Java、C# 的类变量默认复制对象引用不同。此处只有整数成员，编译器生成的复制和析构行为已足够。持有资源时优先使用 `std::string`、容器或智能指针，让成员自行管理生命周期，这叫 Rule of Zero；不要给每个类机械地手写析构函数。需要自定义资源所有权时，再整体设计复制、移动与析构。

`private` 还允许友元访问，不能作为加密或安全隔离机制。当前练习验证封装计算；构造失败、复制语义和资源管理属于本节补充内容。
""", "https://eel.is/c++draft/class.base.init", "25 25\n"),
    "cpp-oop/inheritance": ("""
`public` 继承允许在需要基类引用的位置使用派生对象。基类的私有成员仍存在于对象中，但派生类不能直接访问；应通过基类提供的操作维护其约束。`protected` 扩大了派生类的访问范围，并不等于对外公开。`class` 未写继承方式时默认 private，`struct` 默认 public。

上一例 `salary()` 没有 virtual，因此 Manager 的同名函数是隐藏，不是运行期重写。下面同时展示二者差别：

```cpp
#include <iostream>
struct Employee {
    virtual ~Employee() = default;
    int level() const { return 1; }
    virtual int salary() const { return 100; }
};
struct Manager : Employee {
    int level() const { return 2; }
    int salary() const override { return 150; }
};
int main() {
    Manager manager;
    Employee& employee = manager;
    std::cout << manager.level() << ' ' << employee.level() << ' '
              << employee.salary() << '\\n';
}
```

输出 `2 1 150`：非虚调用取决于表达式的静态类型，虚调用遵循实际对象的最终重写。`override` 能发现漏写 const、参数类型错误等签名不匹配。基类无需在每个派生重写中重复写 virtual。

构造时先初始化基类，再初始化成员，最后执行派生构造函数体；析构相反。未显式指定基类初始化时会尝试默认初始化，因此仅在没有可用默认构造等情况下必须显式传参。多继承可能引入名称歧义与菱形基类；先掌握单继承，多个能力优先用小接口组合。当前练习仍聚焦扩展基类计算。
""", "https://eel.is/c++draft/class.virtual", "2 1 150\n"),
    "cpp-oop/polymorphism": ("""
多态依赖对象仍然是派生对象。把派生对象按值复制到基类会丢失派生部分，称为对象切片；指针或引用不执行这种复制。需要让容器拥有不同派生对象时，用 `std::unique_ptr<Base>` 表达唯一所有权，并提供合适的虚析构函数。

```cpp
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
              << owner->notes() << '\\n';
}
```

输出 `88 1 88`。不要把 `std::vector<Base>` 当成保留派生类型的多态容器。抽象基类则根本不能按值创建或复制成独立对象。

构造和析构期间的虚调用只分派到当前正在构造或析构的类层级，不会调用尚未构造或已经析构的派生部分。也不要从这些阶段依赖纯虚调用。`final` 可以禁止进一步重写或派生，它不替代正确的接口设计。运行期多态适合可替换行为；类型在编译期已经确定时，普通函数和模板往往更直接。当前练习测试虚调用，不自动证明切片与所有权知识已经掌握。
""", "https://eel.is/c++draft/class.cdtor", "88 1 88\n"),
    "cpp-core-memory/pointers": ("""
指针包含地址，不能仅靠“非空”证明对象仍活着。它可能指向局部变量、数组元素或动态对象；只有明确拥有由匹配 new 创建的对象时，才应负责 delete。指向普通局部变量的指针只是借用，不能释放。

```cpp
#include <iostream>
void increase(int* value) {
    if (value != nullptr) ++*value;
}
int main() {
    int first = 4, second = 9;
    const int* read_only = &first;
    read_only = &second;  // 可以改指向，不能通过它改对象
    int* const fixed = &first;
    *fixed = 6;          // 可以改对象，不能改 fixed 的指向
    increase(fixed);
    increase(nullptr);
    std::cout << first << ' ' << *read_only << '\\n';
}
```

输出 `7 9`。`const int*` 与 `int* const` 分别限制所指对象和指针本身，也可组合成 `const int* const`。`nullptr` 具有专用类型，比整数 0 更明确。

指针加减只应在同一数组及其尾后位置范围内使用；尾后指针可比较、可作终止标记，不能解引用。返回局部对象地址、容器扩容后继续用旧元素地址、释放后再访问都会导致悬垂。把某一个指针设空不会修复其他别名。当前交换练习假定传入有效地址，真实接口还应说明是否允许空值；必须有对象时可选择引用参数。
""", "https://eel.is/c++draft/basic.compound", "7 9\n"),
    "cpp-core-memory/references": ("""
引用初始化后绑定到同一对象，之后的赋值是在改对象的值。引用不提供空值状态，但仍可能悬垂；因此“引用一定安全”是错误的。其生存期通常不会自动延长被引用对象的生存期。

```cpp
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
    std::cout << first << ' ' << second << ' ' << length(message) << '\\n';
}
```

输出 `8 10 3`，证明 alias 没有改绑到 second。输入参数用 `const T&` 可以借用较大对象且不允许通过该引用修改；需要修改用 `T&`；小型数值常直接按值传递。

局部 const 引用直接绑定临时对象时可延长该临时对象生存期，但返回函数内部局部变量的引用仍然错误；不要把这个规则推广为“所有间接引用都延寿”。`auto copy = container.front()` 复制元素，`auto& item = container.front()` 引用元素，前提是容器非空。`T&&` 是右值引用，移动操作是另一个主题；`std::move` 只产生相应的值类别转换，本身不保证发生资源搬移。
""", "https://eel.is/c++draft/dcl.ref", "8 10 3\n"),
    "cpp-advanced/templates": ("""
模板不是在运行时把对象都转换成某一种共同基类。它把类型差异留到编译期检查，因此同一逻辑可以得到多个具体实例。模板只有在实际使用相应操作时才要求类型满足这些操作，并非“对任何类型都有效”。

```cpp
#include <iostream>
#include <string>
template<class T>
class Box {
    T value_;
public:
    explicit Box(const T& value) : value_(value) {}
    const T& get() const { return value_; }
};
template<class T>
T larger(T first, T second) { return first < second ? second : first; }
int main() {
    Box<std::string> label("orbit");
    std::cout << larger(3, 7) << ' ' << larger<double>(3, 2.5)
              << ' ' << label.get() << '\\n';
}
```

输出 `7 3 orbit`。`larger(3, 2.5)` 的两个参数会推导出冲突的 T，因此这里显式选择 double。模板不能代替理解数值转换；把 double 强制选成 int 可能丢失小数。

函数模板与类模板分别生成函数和类型；不同 `Box<T>` 是不同类型。一般将模板定义放在头文件，供实例化处看到；显式实例化是可选的工程组织方式。C++20 的 concepts/requires 可把“可比较”等要求写出来，但本课程既有运行练习按当前项目工具链标准执行，本节不要求升级编译标准。练习覆盖函数模板比较，类模板与约束需要另做练习才能评估。
""", "https://eel.is/c++draft/temp", "7 3 orbit\n"),
    "cpp-advanced/dynamic-memory": ("""
先区分对象生存期与存储期：裸指针变量离开作用域只销毁指针本身，不会自动释放它指向的动态对象。所有权必须清晰，借用对象的观察指针不能重复释放资源。动态长度优先 `std::vector`，独占单个对象优先 `std::unique_ptr`，确实需要共同拥有时才考虑 `std::shared_ptr`。

```cpp
#include <iostream>
#include <memory>
#include <utility>
int main() {
    auto owner = std::make_unique<int>(7);
    int* observer = owner.get();
    auto next_owner = std::move(owner);
    std::cout << (owner == nullptr) << ' ' << *next_owner << ' '
              << *observer << '\\n';
}
```

输出 `1 7 7`：所有权移动了，对象地址没有因这次移动而变化。observer 的有效期取决于所指对象是否仍然存活；再次移动所有权不会使它失效。reset 或最终所有者析构并删除对象后，observer 才成为悬垂指针。release() 仅放弃所有权而不删除对象，调用方必须安排后续接管或释放。不要对仍由 unique_ptr 拥有的 get() 借用地址手动 delete。

资源获取即初始化（RAII）把释放责任绑定在对象析构上，正常返回和异常展开都可触发清理。智能指针解决其拥有对象的释放责任，不会消除所有悬垂别名、并发错误或 shared_ptr 循环引用。普通 new 分配失败通常抛出 `std::bad_alloc`，不是返回空指针；`std::nothrow` 形式才按对应约定返回空。不要使用未初始化的 new int[n] 元素；需要清零可使用值初始化或容器。当前练习保留手工分配配对训练，项目代码优先使用自动管理的容器和所有者。
""", "https://eel.is/c++draft/expr.new", "1 7 7\n"),
    "cpp-advanced/exceptions": ("""
异常路径也必须保持对象有效并释放已取得的资源。栈展开会按构造完成的逆序销毁需要清理的局部对象；裸指针所指对象不会因此自动删除。用 RAII 管理资源比在每一个 catch 里重复清理更可靠。

```cpp
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
            std::cout << value << '\\n';
        } catch (const std::invalid_argument&) {
            std::cout << "invalid\\n";
        } catch (const std::out_of_range&) {
            std::cout << "range\\n";
        }
    }
}
```

输出依次为 `42`、`invalid`、`range`。`stoi("42x")` 本身允许只解析前缀，本例通过 used 拒绝尾随字符；它也接受某些前导空白和符号，若协议禁止这些，需要额外定义并检查格式。

这个 parse_all 示例增加了整串解析合同；当前练习仍按 std::stoi 的前缀解析规则处理，并未要求上述尾随字符检查。例如练习输入 `42x` 时，std::stoi 得到 42，按题意输出两倍值 84；不能把补充案例的更严格规则直接当成旧练习要求。

按 `const std::exception&` 捕获可避免按值复制造成切片；catch 顺序从具体到一般。`throw;` 在处理器内保留原异常重新抛出；`throw error;` 会重新创建异常并可能丢失派生类型。基本保证要求失败后对象仍有效且不泄漏，强保证进一步要求失败不改变可观察状态；选哪一种要由操作契约说明。异常展开中析构函数再次向外抛出通常会终止程序，因此析构负责清理，应避免向外传播异常。
""", "https://eel.is/c++draft/except.ctor", "42\ninvalid\nrange\n"),
    "cpp-core-memory/vector": ("""
`size()` 是实际构造的元素个数，`capacity()` 是重新分配前可容纳的元素数；预留空间不是创建元素。`reserve(10)` 之后仍不能直接访问第一个不存在的元素，`resize(10)` 才会把长度改为十。

```cpp
#include <iostream>
#include <vector>
int main() {
    std::vector<int> values;
    values.reserve(8);
    std::cout << values.size() << ' ' << (values.capacity() >= 8) << '\\n';
    values.resize(3, 2);
    values.push_back(5);
    int total = 0;
    for (const int value : values) total += value;
    std::cout << values.size() << ' ' << total << '\\n';
}
```

输出为 `0 1`、`4 11`。capacity 的具体增长倍数不是标准保证，不能用“总是翻倍”设计程序。尾部追加的摊还复杂度为常数，但某一次重新分配仍可能移动或复制所有现有元素。

追加导致重分配时，旧元素指针、引用、迭代器全部失效；未重分配时尾后迭代器仍失效，不能靠 reserve 就在范围 for 中随意追加。只需生成扩展结果时，可先保存原长度并按索引读取、将新结果放进另一容器，或先完成遍历再追加。这里的整数副本遍历不涉及元素所有权；若要修改元素应明确使用 `auto&`，只读复杂对象可用 `const auto&`。
""", "https://eel.is/c++draft/vector.capacity", "0 1\n4 11\n"),
    "cpp-stl-containers/vector": ("""
掌握追加后，还需要区分删除与失效。erase 会移动后续元素，返回被删元素之后的新位置；循环删除时必须接住这个返回值，不能继续递增旧迭代器。

```cpp
#include <iostream>
#include <vector>
int main() {
    std::vector<int> values{1, 2, 3, 4, 5};
    for (auto it = values.begin(); it != values.end();) {
        if (*it % 2 == 0) it = values.erase(it);
        else ++it;
    }
    for (int value : values) std::cout << value << ' ';
    std::cout << '\\n';
}
```

输出 `1 3 5`。erase 会使删除位置及之后的引用和迭代器失效；尾后迭代器也包括在内。没有重新分配的 insert 也会使插入位置及之后的引用和迭代器失效；发生重新分配则全部失效。`clear()` 清空元素，不保证释放 capacity；`shrink_to_fit()` 也只是非强制的收缩请求。

vector 的中间插入和删除通常需要线性移动，但不能据此自动断言链表一定更快：查找位置、缓存局部性和分配成本都影响实际性能。先选择符合访问方式的简单容器，再用代表性数据测量。当前练习仍是尾插与首尾查询，删除循环是补充案例。
""", "https://eel.is/c++draft/vector.modifiers", "1 3 5 \n"),
    "cpp-oop/interfaces": ("""
“接口”是设计角色，C++ 没有强制所有成员纯虚、禁止数据或实现的 interface 语法。常见的纯接口写法是公开虚析构加纯虚操作；抽象基类也可以提供状态与共同实现。前面的默认析构本身就已经是一个实现。应按调用方需要确定职责，而不是把设计惯例误记为语言限制。

```cpp
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
    std::cout << twice(reader) << '\\n';
}
```

输出 `12`。twice 只依赖读取能力，替换实现不必修改调用方。抽象类不能直接创建完整对象；派生类若仍有未提供最终具体重写的纯虚函数，也仍是抽象类。具体实现可以来自中间基类，不要求每个末级类都把所有函数重新写一次。签名应注明参数、返回值和失败语义，“能编译”不代表不同实现具有相同业务契约。
""", "https://eel.is/c++draft/class.abstract", "12\n"),
}

CORRECTIONS = {
    "cpp-oop/classes": [("private 成员只能被成员函数访问", "private 成员通常由本类成员函数或友元访问"), ("const 成员函数承诺不修改对象状态", "const 成员函数限制通过 this 修改非 mutable 数据成员")],
    "cpp-oop/inheritance": [("派生类构造函数必须通过初始化列表调用基类构造函数", "需要给基类构造函数传参时，应在派生类初始化列表中显式指定"), ("在派生类中重写方法改变默认实现。", "在派生类中扩展行为，并区分同名隐藏与虚函数重写。")],
    "cpp-stl-containers/vector": [("理解 vector 连续存储与倍增扩容。", "理解 vector 连续存储与按需扩容。"), ("容量不足时自动倍增扩容（迭代器失效）", "容量不足时自动扩容（增长倍数由实现决定，重分配使迭代器失效）")],
    "cpp-advanced/dynamic-memory": [("从根源消除这两类缺陷", "自动管理所有权对应的释放责任，但仍需避免悬垂借用")],
    "cpp-oop/interfaces": [("由\"全部成员函数为纯虚、无数据成员\"的抽象类承担接口角色：只描述能力契约（能做什么），不包含实现", "常用带纯虚操作的抽象基类表达能力契约；是否包含状态和共同实现由设计决定"), ("不要在接口里放数据成员或具体实现（退化为普通基类）", "纯接口通常保持小而聚焦；需要共享状态与实现时可采用抽象基类"), ("实现类必须实现全部纯虚函数才能创建对象", "具体类必须为全部纯虚函数提供最终的具体重写（可继承已有实现）才能创建对象")],
}

def main():
    audit = Path(__file__).parent
    manifests = []
    for key, (addition, source, expected) in LESSONS.items():
        path = ROOT / 'content/cpp' / f'{key}.md'
        text = path.read_text(encoding='utf-8-sig')
        if MARKER in text:
            raise SystemExit(f'Refusing duplicate pass: {path}')
        for before, after in CORRECTIONS.get(key, []):
            if before not in text:
                raise SystemExit(f'Correction source missing: {key}: {before}')
            text = text.replace(before, after)
        text = text.rstrip() + '\n\n' + MARKER + '\n\n' + addition.strip() + f'\n\n延伸核对：[C++ 标准草案相关条款]({source})。以上是本课程原创示例与讲解，条款用于核对语言语义。\n'
        path.write_text(text, encoding='utf-8', newline='\n')
        code = re.search(r'```cpp\n(.*?)\n```', addition, re.S).group(1)
        sample = audit / 'examples' / f'{key.replace("/", "--")}.cpp'
        sample.parent.mkdir(parents=True, exist_ok=True)
        sample.write_text(code + '\n', encoding='utf-8')
        manifests.append({'lesson':key,'example':str(sample.relative_to(ROOT)).replace('\\','/'),'expected':expected,'source':source})
    (audit/'examples.json').write_text(json.dumps(manifests, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Expanded {len(manifests)} C++ lessons; exercise JSON untouched.')

if __name__ == '__main__':
    main()
