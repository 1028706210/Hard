---
id: python-capstone-ai-draw
title: AI 绘画任务的离线规格
concepts: [collections, functions, security]
objectives: [把绘画提示词整理为可审查的本地任务规格, 在调用外部生成器前验证尺寸与安全字段]
prerequisites: [python-capstone-openai]
difficulty: advanced
experience_points: 40
source_url: https://www.runoob.com/python3/python-ai-draw.html
source_snapshot_date: 2026-08-23
---

# 生成前的可验证步骤

图像生成常包含远程模型、账户配额和内容规则，不能在安全 Runner 中执行。课程练习只构造离线规格：提示词、尺寸和用途均是普通数据，不下载图片也不联系服务。

```python
job = {"prompt": "蓝色纸飞机", "width": 512, "height": 512}
print(job["width"] == job["height"])
```

规格函数应拒绝空提示词与不支持的尺寸。这样在真正调用提供方前，错误就能被本地测试捕获，也能留下审计友好的输入记录。

```python
def valid_size(width, height):
    return (width, height) in {(512, 512), (768, 512)}

print(valid_size(512, 512))
```

真实生成器、令牌和图片 URL 都属于部署环境；本课只验证它们之前的确定性逻辑。


## 概念定义与适用场景

AI 绘画任务的离线规格解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
