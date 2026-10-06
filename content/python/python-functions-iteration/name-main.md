---
id: python-functions-iteration-name-main
title: Python __name__
concepts: [functions, tooling]
objectives: [解释模块直接运行和被导入的差异, 使用 __name__ 守卫隔离启动行为]
prerequisites: [python-functions-iteration-decorators]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-name-main.html
source_snapshot_date: 2026-08-23
---

# 区分导入和入口

模块直接运行时 `__name__` 为 `__main__`，被导入时则是模块名。把命令行入口放进守卫，可以让导入只提供函数而不触发副作用。

```python
if __name__ == "__main__":
    print("run directly")
```

可复用的核心逻辑应放在普通函数中。

```python
def main():
    return "ready"
print(main())
```


## 概念定义与适用场景

Python __name__解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
