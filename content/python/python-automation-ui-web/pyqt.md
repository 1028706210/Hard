---
id: python-automation-ui-web-pyqt
title: Python PyQt 界面状态
concepts: [collections, security]
objectives: [用纯函数维护界面可见状态, 在不启动 GUI 的前提下验证用户操作结果]
prerequisites: [python-automation-ui-web-markdown]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-pyqt.html
source_snapshot_date: 2026-08-23
---

# 把界面逻辑从窗口中拿出来测试

窗口、事件循环和系统显示器不属于 Runner 的安全练习范围。先把按钮点击后的状态变化写成纯函数，再由真实应用把它连接到 PyQt 的 signal 和 slot。

```python
def can_save(title):
    return bool(title.strip())

print(can_save("学习计划"))
```

界面提示不能代替输入校验；保存前仍应拒绝空标题。返回副本而不是原地修改状态，能够让取消与重试有可验证的边界。

```python
def apply_save(state, title):
    return {**state, "saved": True} if can_save(title) else dict(state)

print(apply_save({"saved": False}, ""))
```

## 概念定义与适用场景

把界面条件抽成纯函数，可以独立验证空标题和正常标题。按钮可点击并不表示保存请求成功，本课只计算条件，不创建窗口或写入数据。

## 语法、API 与边界

读取标题文本，can_save(title) 返回去掉首尾空白后是否非空，输出 True 或 False。中文和 __invalid__ 都是普通文本；空白标题为 False，退出码0。只验证保存按钮条件，不启动 GUI。

模块挑战：输入JSON对象，state必须是含布尔saved字段的对象，title必须为字符串。apply_action返回state副本，标题去掉空白后非空则把副本saved设为True，否则保留原值。逐行输出新状态saved和原状态saved，证明未修改输入。错误结构无输出，退出码1；不启动GUI。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
