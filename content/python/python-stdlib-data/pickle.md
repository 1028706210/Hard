---
id: python-stdlib-data-pickle
title: Python Pickle
concepts: [io, security]
objectives: [理解 pickle 仅适用于受信数据, 选择 JSON 作为跨边界交换格式]
prerequisites: [python-stdlib-data-sys]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-pickle.html
source_snapshot_date: 2026-08-23
---

# 不反序列化不受信对象

pickle 能保存 Python 对象，但加载不受信字节可能执行危险行为。跨网络、导入包和用户上传数据应使用受限、可验证的格式，而不是 pickle。

```python
import pickle
data = pickle.dumps([1, 2])
print(len(pickle.loads(data)))
```

本课示例只处理代码内创建的受信字节。

```python
import pickle
print(pickle.loads(pickle.dumps("Hard")))
```


## 概念定义与适用场景

Python Pickle解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
