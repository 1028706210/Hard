---
id: python-foundations-package-management
title: 用 pip 管理依赖
concepts: [packages, environments]
objectives:
  - 区分包名称、版本约束与安装命令。
  - 在安装前先确认项目环境，避免污染全局解释器。
prerequisites: [python-foundations-virtual-environment]
difficulty: beginner
experience_points: 35
source_url: https://www.runoob.com/python3/python3-pip.html
source_snapshot_date: 2026-08-23
---

# 依赖是项目的一部分

pip 负责把 Python 包安装到当前选定环境。安装前先确认环境，再阅读包名和版本要求；“能装上”不等于“适合项目”。课程 Runner 不会联网安装包，相关练习只处理版本文本和依赖声明。

```python
package = "example-tool"
print(f"依赖: {package}")
```

固定版本可以提高可重复性，但升级时仍应通过测试确认兼容性。把需求写清楚，比依赖某台电脑已有的包更可靠。

```python
requirement = "example-tool==1.0"
print(requirement.split("==")[0])
```

不要执行来历不明的安装命令，也不要把开发机缓存当作发布物。


## 概念定义与适用场景

用 pip 管理依赖解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
