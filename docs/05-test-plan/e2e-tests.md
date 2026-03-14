# 端到端测试用例

> Phase 5 | 创建时间: 2026-03-15

## 核心用户路径 E2E

| # | 用例名称 | 层级 | 路径类型 | 步骤 | 预期结果 | 断言要点 |
|---|---------|------|---------|------|---------|---------|
| 1 | 完整对话流程 | e2e | Happy Path | 1.登录 2.选 Claude Code 模式 3.发送"say hello" 4.等待响应 | 收到流式响应，包含文本 | SSE 流有 answer_chunk + task_done |
| 2 | 模式切换 | e2e | Happy Path | 1.Claude Code 模式发消息 2.切换 Research 3.发消息 | 两种模式都正常响应 | 两次 mode 不同，均收到 task_done |
| 3 | 首次实例创建 | e2e | Happy Path | 1.新用户注册 2.首次发送任务 | 实例自动创建 + 响应 | instanceStatus=running, 响应非空 |
| 4 | Credits 耗尽停机 | e2e | Happy Path | 1.设置 credits=0 2.发送任务 | 拒绝执行并提示充值 | 返回 quota_limit 错误 |
| 5 | 对话历史持久化 | e2e | Happy Path | 1.发送任务 2.刷新页面 3.查看历史 | 历史记录存在 | 之前的对话可见 |
