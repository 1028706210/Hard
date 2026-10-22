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

完整规格应包含输入提示词和尺寸，只输出固定尺寸不能证明处理了输入。JSON用于表示数据，不会自动触发生成器；尺寸是本题约定，不代表某提供方的实时支持清单。

## 语法、API 与边界

读取非空提示词，去掉首尾空白并保留内部空格。make_job(prompt) 返回包含 prompt 和固定 size=512x512 的字典，以 json.dumps(ensure_ascii=False, sort_keys=True) 输出整个规格。空白输入无输出，退出码1。只生成本地数据，不生成或下载图片、不调用模型。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
