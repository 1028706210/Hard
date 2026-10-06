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

PyQt 把窗口控件、信号和事件循环连接为桌面界面。可测试性来自先把界面状态转换拆成纯函数：同样的标题和旧状态应得到同样的新状态，控件只负责把用户动作转交给该函数。

## 语法、API 与边界

真实程序会把按钮的 signal 连接到 slot，再更新 widget；课程不启动事件循环或 GUI，而用 `can_save`、`apply_action` 这类函数验证输入校验和不可变状态副本。空白标题是正常边界，不应创建保存动作。

## 常见错误与实践建议

不要让按钮文案代替业务校验，也不要直接修改共享状态后失去回滚能力。测试可保存、不可保存和保留状态三个分支；真实界面还应提供键盘可操作性、错误文字和关闭确认。
