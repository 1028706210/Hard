---
id: python-flow-collections-for-loop
title: Python for 循环
concepts: [control-flow, collections]
objectives: [用 for 遍历序列, 使用 range 构造有限次数的循环]
prerequisites: [python-flow-collections-data-structures]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-for.html
source_snapshot_date: 2026-08-23
---

# 按元素或次数遍历

`for` 适合已知序列和有限范围。循环变量只代表当前元素；不要依赖它在循环结束后仍承担原来的业务含义。

```python
for letter in "Hi":
    print(letter)
```

`range` 产生一个受控的整数序列，终点本身不包含在内。

```python
for index in range(3):
    print(index)
```


## 概念定义与适用场景

Python for 循环解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
