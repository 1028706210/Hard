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

Selenium 的 WebDriver 通过定位器查找页面元素，再执行点击、输入、读取等用户操作。可靠测试优先使用稳定的 `data-testid` 或可访问名称，而不是易变的样式类；等待条件必须描述元素何时真正可交互。

## 语法、API 与边界

典型流程是创建 driver、用显式等待取得 element、执行 action、在 `finally` 中 `quit()`。本课用本地 fake driver 模拟 `find_element`、等待、`click` 和关闭，因此验证的是调用顺序与失败处理，不下载浏览器驱动也不打开 GUI。

## 常见错误与实践建议

不要用固定 sleep 替代等待，也不要在找不到元素后继续宣称成功。测试保存按钮、另一个合法按钮和缺失定位器，确认关闭操作总会发生；真实浏览器测试仍需独立的受控环境。
