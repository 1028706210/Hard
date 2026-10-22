---
id: python-automation-ui-web-selenium
title: Python selenium 选择器设计
concepts: [security, collections]
objectives: [为稳定页面元素选择合适定位策略, 使用本地 DOM fixture 验证选择器意图]
prerequisites: [python-automation-ui-web-pyecharts]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-selenium.html
source_snapshot_date: 2026-08-23
---

# 自动化从可测试的定位开始

浏览器自动化应优先使用稳定的 `data-testid`，而不是易变的样式类名。课程以本地 fake WebDriver 表达 `find_element`、点击和关闭语义：不下载驱动、不启动浏览器。

```python
class FakeDriver:
    def find_element(self, selector):
        if selector != "[data-testid=save]":
            raise LookupError(selector)
        return {"selector": selector}

print(FakeDriver().find_element("[data-testid=save]")["selector"])
```

显式等待的职责是“直到条件成立再操作”；无论成功还是失败，WebDriver 都必须在 `finally` 中关闭。

```python
events = []
try:
    events.append("wait:save")
    events.append("click:save")
finally:
    events.append("quit")
print(events)
```

## 概念定义与适用场景

本地模拟器验证定位、点击和 finally 关闭分支，不能模拟浏览器加载、DOM 变化或真实显式等待。失败也要输出关闭状态，避免只测试成功流程。

## 语法、API 与边界

使用已提供的本地 Driver 模拟器。读取选择器并去掉首尾空白，只有 [data-testid=save] 和 [data-testid=cancel] 存在。查找成功后调用 click，最后无论成功失败都 quit。成功输出 click:选择器|closed=True；未知选择器（含空输入）输出 missing|closed=True，退出码 0。不启动真实浏览器，不把模拟查找称为实际等待验证。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
