---
id: python-foundations-virtual-environment
title: 为项目隔离虚拟环境
concepts: [environments, packages]
objectives:
  - 说明虚拟环境如何避免项目依赖互相干扰。
  - 记录项目所需依赖，而不把环境目录当作源码提交。
prerequisites: [python-foundations-installation]
difficulty: beginner
experience_points: 35
source_url: https://www.runoob.com/python3/python-venv.html
source_snapshot_date: 2026-08-23
---

# 每个项目有自己的依赖边界

虚拟环境把某个项目的第三方包与全局环境分开。这样 A 项目升级一个库时，不会意外改变 B 项目的行为。创建和激活属于本机开发步骤；练习代码只演示可验证的数据逻辑，不会自行创建环境目录。

```python
environment_name = "study-env"
print(f"环境: {environment_name}")
```

依赖清单应描述“项目需要什么版本”，而不是复制整个虚拟环境。换到新机器时，清单让安装过程可重放。

```python
requirements = ["formatter", "test-runner"]
print(len(requirements))
```

不要把密钥、缓存或机器专属绝对路径放进依赖文件。


## 概念定义与适用场景

为项目隔离虚拟环境解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
