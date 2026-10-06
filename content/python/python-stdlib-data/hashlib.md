---
id: python-stdlib-data-hashlib
title: Python hashlib
concepts: [strings, functions]
objectives: [计算文本的摘要, 理解摘要不是可逆加密]
prerequisites: [python-stdlib-data-statistics]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-hashlib.html
source_snapshot_date: 2026-08-23
---

# 用摘要核对内容

摘要把字节映射为固定长度标识，适合完整性核对而非保密。相同输入会产生相同摘要，因此敏感数据不能只靠哈希保护。

```python
import hashlib
print(hashlib.sha256(b"Hard").hexdigest()[:4])
```

编码必须在调用摘要函数前明确。

```python
import hashlib
print(len(hashlib.sha256("x".encode()).hexdigest()))
```


## 概念定义与适用场景

Python hashlib解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
