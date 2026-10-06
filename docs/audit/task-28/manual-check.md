# Task 28 人工抽查记录

- 八条来源均映射到唯一课时；网络、邮件和 HTTP 使用本地 fixture，子进程使用纯命令计划，所有外部边界均保持禁用。
- `asyncio` 参考解真实运行 `async def`、`await`、`asyncio.run` 与取消分支；`threading` 参考解以有限本地线程和 `Lock` 验证临界区；subprocess 题不导入或执行子进程，不会开放 Runner 权限。
- 每课具备原创中文正文、两个示例、三道知识题和可执行题；asyncio 课包含模块挑战。
- 公开内容只包含题面、starter code 与可见说明；私有参考解和隐藏用例不进入公开响应。
