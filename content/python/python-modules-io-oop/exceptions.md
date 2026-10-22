---
id: python-modules-io-oop-exceptions
title: Python 错误和异常
concepts: [exceptions, functions]
objectives: [用 try 和 except 处理可预期失败, 避免吞掉未知异常]
prerequisites: [python-modules-io-oop-os]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python3-errors-execptions.html
source_snapshot_date: 2026-08-23
---

# 只处理知道如何恢复的错误

异常表示正常流程之外的失败。捕获具体异常并给出明确恢复方式，比宽泛捕获所有错误更安全；未知失败应保留诊断路径。

```python
try:
    value = int("x")
except ValueError:
    value = 0
print(value)
```

`finally` 用于不论成功与否都要执行的有限清理动作。

```python
try:
    print("work")
finally:
    print("done")
```

## 异常如何沿调用链传播

语法错误通常在解析时发现，运行时异常则在执行相应表达式时发生。异常会中断当前正常流程，沿调用栈寻找匹配处理器；没有处理器时保留回溯并终止。处理器按顺序匹配，具体子类应放在宽泛基类前；`except Exception` 不会捕获所有 `BaseException` 子类，例如 `KeyboardInterrupt` 和 `SystemExit`。

`else` 只在 `try` 正常完成时运行，适合放只应在成功后执行的操作。它抛出的异常不会被同一个 `try` 前面的 `except` 捕获。`finally` 在正常结束、异常传播或 `return` 离开时用于清理，但不能保证在进程被强制终止时仍执行。

```python
def read_count(text):
    try:
        value = int(text)
    except ValueError as error:
        print(type(error).__name__)
        return None
    else:
        print("parsed")
        return value
    finally:
        print("finished")

print(read_count("5"))
print(read_count("bad"))
```

预期输出：

```text
parsed
finished
5
ValueError
finished
None
```

## 主动报告错误与保留原因

`raise` 主动抛出异常，无参数的 `raise` 在处理器中重新抛出当前异常。业务层可定义继承自 `Exception` 的异常，并使用 `raise NewError(...) from error` 在转换错误含义时保留原因。不要只打印错误后返回一个伪造成功值。

```python
class CountError(Exception):
    pass

def positive_count(text):
    try:
        value = int(text)
    except ValueError as error:
        raise CountError("count must be an integer") from error
    if value <= 0:
        raise CountError("count must be positive")
    return value

try:
    positive_count("bad")
except CountError as error:
    print(str(error))
    print(type(error.__cause__).__name__)
```

预期输出：

```text
count must be an integer
ValueError
```

`try` 应只包住打算处理的失败操作；范围过大可能把程序缺陷误认为输入错误。不要在 `finally` 中 `return` 或抛出无关异常，会覆盖原有结果或失败信息。文件、锁等资源优先使用其上下文管理器清理；不要以 `assert` 代替外部输入校验，优化执行时断言可能被移除。

技术参考：[官方异常处理教程](https://docs.python.org/3.14/tutorial/errors.html)、[内建异常层次](https://docs.python.org/3.14/library/exceptions.html)。现有练习特意规定转换失败恢复为零，下面保留该规则；它不是业务异常的通用处理方案。

## 概念定义与适用场景

异常处理只恢复知道如何处理的失败。本题把文本转整数的 ValueError 定义为可恢复错误，恢复结果为 0；这不是所有程序都应采用的默认策略。

## 语法、API 与边界

try 中只放 int(text)，except ValueError 设置恢复值，最后统一输出。int 不接受小数文本，不应先 float 再截断。其他系统或程序错误不在本题的恢复范围内。

## 常见错误与实践建议

不要保留特殊字符串作为隐藏异常分支，也不要裸 except。输出 0 的恢复规则会让真实零和转换失败得到相同结果，调用者若需区分二者，应另行设计接口；当前题面明确只要求一个整数。
