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

pickle 可以保存 Python 对象，但加载不可信字节可能执行代码。本题只将已验证的整数列表在内存中往返转换，加载的字节由本程序直接生成。

## 语法、API 与边界

JSON 是输入边界，类型检查使用 type(value) is int 来排除布尔值。序列化结果是字节序列，长度并不等于列表元素数量；应统计还原对象。

## 常见错误与实践建议

不要为了通过练习去加载用户提供的 pickle 或 base64 字节。验证普通、重复和空列表，自动输出测试不能单独证明提交采用了指定序列化 API。
