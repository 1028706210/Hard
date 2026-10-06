---
id: python-functions-iteration-scope
title: Python 命名空间与作用域
concepts: [variables, functions]
objectives: [区分局部和全局名称, 避免函数意外修改外层状态]
prerequisites: [python-functions-iteration-name-main]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python3-namespace-scope.html
source_snapshot_date: 2026-08-23
---

# 名称在边界内生效

函数内部创建的名称默认是局部名称，只在调用期间可见。优先用参数和返回值传递状态，能减少全局变量带来的隐藏依赖。

```python
value = "outer"
def show():
    value = "inner"
    return value
print(show())
```

同名名称在不同作用域中可以独立存在。

```python
name = "Hard"
def local_name():
    name = "Learner"
    return name
print(local_name())
```


## 概念定义与适用场景

Python 命名空间与作用域解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
