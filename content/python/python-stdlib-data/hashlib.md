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

摘要由输入字节决定，SHA-256 的十六进制表示长度始终为 64。只打印长度不能说明程序计算了哪份内容的摘要，因此本题要求完整摘要。

## 语法、API 与边界

encode("utf-8") 把文本转换为明确字节，sha256 计算摘要，hexdigest 返回可显示的十六进制字符串。空内容也有有效摘要；空格、编码或内部换行变化都会改变参与计算的字节。

## 常见错误与实践建议

不要使用 Python 的 hash 代替 SHA-256，也不要先 strip 导致首尾空格消失。摘要不是可逆加密，不能用固定长度或样例前缀冒充计算结果。
