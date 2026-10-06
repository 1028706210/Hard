---
id: python-functions-iteration-iterators
title: Python 迭代器与生成器
concepts: [collections, functions]
objectives: [识别可迭代对象和迭代器的区别, 使用生成器逐步产生值]
prerequisites: [python-flow-collections-while-loop]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python3-iterator-generator.html
source_snapshot_date: 2026-08-23
---

# 按需取得下一个值

可迭代对象可被 `for` 遍历，迭代器负责给出下一个值。生成器函数通过 `yield` 延迟产生数据，适合不必一次保存全部结果的场景。

```python
for value in [1, 2]:
    print(value)
```

生成器的每次恢复都从上一次 `yield` 后继续。

```python
def steps():
    yield 1
    yield 2
print(list(steps()))
```


## 概念定义与适用场景

Python 迭代器与生成器解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
