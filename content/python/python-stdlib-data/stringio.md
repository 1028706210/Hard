---
id: python-stdlib-data-stringio
title: Python StringIO
concepts: [io, strings]
objectives: [在内存中读写文本流, 用 StringIO 测试不需真实文件的输出]
prerequisites: [python-stdlib-data-queue]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-stringio.html
source_snapshot_date: 2026-08-23
---

# 用内存模拟文本流

StringIO 提供类似文件的文本接口，但数据只保存在内存。这适合隔离输出格式测试，不应误当作持久化存储。

```python
from io import StringIO
stream = StringIO(); stream.write("Hard")
```

读取前应回到流的开头。

```python
from io import StringIO
stream = StringIO("ready")
print(stream.read())
```

## 概念定义与适用场景

StringIO 在内存中提供文件式接口，数据不会自动保存到磁盘。write 会推进游标，因此写完直接 read 通常读不到刚写入的内容。

## 语法、API 与边界

seek(0) 把游标移回开头，再 read 获取内容。与文件课一样，仅删除末尾换行，空格和内部换行仍属于正文。

## 常见错误与实践建议

遗漏 seek 会得到空输出；getvalue 可获取全部内容，但不能用它来推断游标已回到开头。练习应观察写入、定位、读取三个步骤。
