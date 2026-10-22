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

隔离环境的价值在于让项目各自记录依赖，而不是共享一份碰巧可用的全局安装。清单比复制环境目录更容易复查。本练习只整理名称，不能证明依赖已安装。

## 语法、API 与边界

读取支架提供 dependencies 列表；set(dependencies) 可以去掉完全相同的重复项，再用 len 计数。空白行忽略，空清单是零。此处按大小写敏感的文本计数，不是 pip 的包名解析器。

## 常见错误与实践建议

不要把空白行算成包，也不要把重复记录当作不同依赖。版本约束如 demo==1.0 属于后续课时，当前练习明确拒绝；不会触发任何安装操作。
