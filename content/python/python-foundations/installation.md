---
id: python-foundations-installation
title: 安装后的第一项检查
concepts: [interpreter, tooling]
objectives:
  - 用版本信息确认终端找到的是预期解释器。
  - 区分“已安装”与“当前终端可运行”。
prerequisites: [python-foundations-introduction]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-install.html
source_snapshot_date: 2026-08-23
---

# 安装不是终点，验证才是

装好 Python 后，先在自己的终端执行版本命令并记录结果。这个动作确认的是当前 shell 找到的解释器，而不是安装向导曾经显示过的版本。项目使用固定工具链时，尤其不要依赖模糊的“应该已经装好”。

```python
version = "3.x"
print(f"Python {version} 已可用于学习")
```

版本号可以作为普通字符串处理；真正的安装和 PATH 修改应由受控的本地工具完成，而不是由学习题目触发。

```python
parts = "3.13".split(".")
print(parts[0])
```

若终端找不到 Python，先检查命令路径和当前环境，不要随意复制未知网站的安装脚本。

## 概念定义与适用场景

真正的安装验证来自本机终端的命令结果；单纯打印一段版本文本不能证明解释器存在。课程题只练习阅读和整理提供的版本记录，不能代替环境检查。

## 语法、API 与边界

本题输入格式固定为 Python 3.次版本.补丁版本，两段版本号只含 ASCII 数字。起始代码负责解析并提供 version；你只需输出整理后的版本。不是所有合法 Python 版本描述都符合这个教学用简化格式。

## 常见错误与实践建议

不要写死 3.13.1，也不要把版本当作小数处理。3.10.12 有三个独立部分；保留完整文本，缺少补丁号或包含额外说明时按题意拒绝。
