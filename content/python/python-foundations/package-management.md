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

依赖声明把包名称和版本约束放在一起。提取包名是理解声明的第一步，不能据此推断兼容性或包是否已经安装；真正安装仍应在选定环境中由用户执行。

## 语法、API 与边界

本题采用教学用子集：包名后必须是 ==，版本仅含主、次两段数字。起始代码解析得到 package 与 version，输出只包含 package。完整 pip 规范允许更多版本和约束形式，不应套用本题的简化校验去验证实际项目需求文件。

## 常见错误与实践建议

简单 split 后取第一项会错误接受缺版本或多个 == 的记录，因此校验由支架明确处理。保持提供的校验，不要忽略错误后照样输出包名，更不要调用安装命令。
