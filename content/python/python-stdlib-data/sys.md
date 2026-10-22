---
id: python-stdlib-data-sys
title: Python sys
concepts: [tooling, io]
objectives: [读取受控的解释器信息, 区分诊断信息与业务输入]
prerequisites: [python-stdlib-data-hashlib]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-sys.html
source_snapshot_date: 2026-08-23
---

# 解释器环境信息

sys 提供与 Python 运行环境相关的接口。业务逻辑不应依赖不稳定的本机路径；诊断应只记录安全、必要的信息。

```python
import sys
print(bool(sys.version_info.major >= 3))
```

命令行参数属于外部输入，仍需验证。

```python
import sys
print(type(sys.argv).__name__)
```

## 概念定义与适用场景

sys.version_info 提供结构化解释器版本，比解析版本展示字符串更直接。当前 Runner 固定为 Python 3；版本升级时需同步复核相关课程预期。

## 语法、API 与边界

required 是业务输入，major 是环境诊断值，两者来源不同。这里只输出比较结果，不暴露安装路径、环境变量或命令行中的潜在秘密。

## 常见错误与实践建议

总是输出 True 会掩盖高版本要求不满足的情况。比较方向应为实际版本大于等于要求，而不是反过来，也不应把输入当成当前环境版本。
