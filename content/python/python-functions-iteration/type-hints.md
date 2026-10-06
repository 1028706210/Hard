---
id: python-functions-iteration-type-hints
title: Python 类型注解
concepts: [types, functions]
objectives: [为函数参数和返回值添加类型注解, 理解注解不会替代运行时校验]
prerequisites: [python-functions-iteration-scope]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python-type-hints.html
source_snapshot_date: 2026-08-23
---

# 把接口意图写出来

类型注解说明函数期望接收和返回的值，便于编辑器和静态检查工具发现不一致。Python 运行时不会自动替你转换或拒绝参数，因此边界校验仍需要代码完成。

```python
def add(left: int, right: int) -> int:
    return left + right
print(add(1, 2))
```

注解应描述稳定的公共接口，而不是掩盖含糊的命名。

```python
def greeting(name: str) -> str:
    return f"Hello, {name}"
print(greeting("Hard"))
```


## 概念定义与适用场景

Python 类型注解解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
