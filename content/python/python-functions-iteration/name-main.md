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

直接执行模块时 __name__ 为 __main__，导入时通常是模块名。入口守卫让命令行读取和打印仅在直接执行时发生；main 函数本身可以由其他模块调用。

## 语法、API 与边界

把纯计算 main(name) 放在守卫之外，读取和打印放在守卫之内。假设代码保存为 entry.py，可直接运行它，再在同目录执行 python -c "import entry; print(entry.main('study'))"；导入本身不应等待输入或额外打印。

## 常见错误与实践建议

不要比较输入名称是否为 __main__，守卫检查的是解释器提供的模块变量。在线 Runner 仅执行脚本，无法据成功状态推断导入没有副作用；两种执行方式需要分别验证。
