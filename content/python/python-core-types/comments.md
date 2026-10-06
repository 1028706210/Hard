---
id: python-core-types-comments
title: Python 注释
concepts: [tooling, variables]
objectives:
  - 用注释解释不容易从代码直接看出的原因。
  - 避免用注释重复代码已经表达的动作。
prerequisites: [python-core-types-basic-syntax]
difficulty: beginner
experience_points: 25
source_url: https://www.runoob.com/python3/python3-comment.html
source_snapshot_date: 2026-08-23
---

# 注释记录选择的理由

注释以 `#` 开头，解释器不会执行它。好的注释补充的是约束、背景或取舍，而不是把 `print` 再描述一遍。代码变化时，也要检查相邻注释是否仍然正确。

```python
# 用户标识来自已验证的本地配置。
user_id = "learner-01"
```

临时调试信息应当及时删除或改成正式说明，避免它变成误导性的历史记录。

```python
total = 2 + 3  # 组合两个已确认的数量
print(total)
```


## 概念定义与适用场景

Python 注释解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
