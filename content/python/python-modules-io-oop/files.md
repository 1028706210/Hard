---
id: python-modules-io-oop-files
title: Python 文件
concepts: [io, exceptions]
objectives: [在受控临时目录中读写文本文件, 使用 with 确保文件句柄关闭]
prerequisites: [python-modules-io-oop-input-output]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python3-file-methods.html
source_snapshot_date: 2026-08-23
---

# 文件操作限定在授权目录

文件句柄是资源，应使用 `with` 明确打开范围。学习题只操作 Runner 临时工作目录中的固定文件名，不读取用户磁盘或系统路径。

```python
from pathlib import Path
Path("note.txt").write_text("ready", encoding="utf-8")
```

读取时指定编码并在边界处理异常。

```python
from pathlib import Path
print(Path("note.txt").read_text(encoding="utf-8"))
```

## 打开模式、编码与资源范围

`open(path, mode, encoding=...)` 返回文件对象，常用模式如下；操作真实文件前应确定路径和写入后果。

| 模式 | 行为 |
| --- | --- |
| `r` | 读取，文件必须存在 |
| `w` | 写入；不存在则创建，存在则先截断内容 |
| `a` | 追加写入，不覆盖已有内容 |
| `x` | 仅新建；已存在时抛出 `FileExistsError` |
| `b` 后缀 | 二进制字节模式，如 `rb`；不传文本编码 |
| `+` 后缀 | 增加读写能力，不改变前面模式的创建/截断语义 |

文本模式读取 `str`，二进制模式读取 `bytes`。跨环境处理文本要明确 `encoding="utf-8"`，不能依赖机器默认编码。`with` 会在正常退出或异常离开时关闭文件，关闭后不能继续读写；它不自动撤销已经写入的数据，也不保证整个写入过程具备事务性。

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "sample.txt"
    with path.open("w", encoding="utf-8") as stream:
        stream.write("read\ntest\n")
    with path.open("a", encoding="utf-8") as stream:
        stream.write("code\n")
    with path.open("r", encoding="utf-8") as stream:
        print(stream.readline().rstrip("\n"))
        print(stream.read().splitlines())
    print(stream.closed)
```

预期输出：

```text
read
['test', 'code']
True
```

本例自行创建并清理临时目录，不覆盖已有用户文件。它是独立教学示例；现有 Runner 练习仍使用题目指定的 `note.txt`。

## 顺序读取、游标与异常

`read()` 从当前位置读到结束，`read(size)` 限制本次读取长度，`readline()` 取一行并保留行末换行。逐行 `for line in stream` 适合不必一次载入全部内容的文件；读取到末尾会返回空字符串，空白行则可能是 `"\n"`，两者不同。

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "sample.txt"
    path.write_text("你好\n", encoding="utf-8")
    with path.open("r", encoding="utf-8") as stream:
        print(stream.read(1))
        print(repr(stream.read()))
        print(repr(stream.read()))
        stream.seek(0)
        print(stream.read().splitlines())
    print(path.read_bytes().decode("utf-8").splitlines())
```

预期输出：

```text
你
'好\n'
''
['你好']
['你好']
```

文本游标的 `tell()` 值是供恢复位置使用的位置标记，不能随意当成 Unicode 字符索引进行偏移。跨平台文本模式通常处理换行转换；CSV 读写应遵循 CSV 课程的 `newline=""` 约定。文件不存在、权限不足和编码不匹配分别可能产生 `FileNotFoundError`、`PermissionError` 和 `UnicodeDecodeError`，应按可恢复范围处理，不能捕获全部错误后假装读取到空文件。`flush()` 推送 Python 的写缓冲，不等同于保证数据已经持久化到物理存储。

技术参考：[官方文件读写教程](https://docs.python.org/3.14/tutorial/inputoutput.html#reading-and-writing-files)、[open](https://docs.python.org/3.14/library/functions.html#open)、[文本与字节流](https://docs.python.org/3.14/library/io.html)。现有练习只检查受控文件的写入与读回；它不验证所有模式、磁盘耐久性或任意路径访问。

## 概念定义与适用场景

文件练习把写入、关闭、重新打开和读取连成完整过程。with 在块退出时关闭句柄，写入完成后再读取，避免缓冲区尚未刷新就检查内容。

## 语法、API 与边界

固定文件 note.txt 仅位于 Runner 的本次临时工作目录；w 覆盖此练习文件，r 读取。编码明确为 UTF-8。strip 会误删空格，题面只允许 rstrip("\n")。NUL 检查是本题的数据规则，不是在声称操作系统禁止文本文件保存 NUL。

## 常见错误与实践建议

输入是文件内容，不是文件路径。__invalid__ 不等于 NUL；用真实的 U+0000 检查失败分支。输出匹配只能验证读回结果，不能独自证明所有提交实际进行了文件读写；参考答案另行检查文件产物。
