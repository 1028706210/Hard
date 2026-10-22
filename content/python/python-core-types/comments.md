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

注释补充代码背后的约定。例如数量为零表示没有项目，不是读取失败。说明这一点比写“下面做加法”更有用；运行结果仍由实际语句决定。

## 语法、API 与边界

练习接收两个非负整数，零也必须参与计算。起始代码处理解析、数量检查及负数拒绝；在这段代码后用 # 注释解释零的含义，再输出两数之和。注释不会生成输出。

## 常见错误与实践建议

不要把 print 写在 # 后面，否则整个语句都会被忽略。自动评分只能核对输出与退出状态，不能评估注释的表达质量；自行确认注释说明了原因，并且与零值规则一致。
