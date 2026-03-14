# 测试计划：Claude Code 代理 API

> Phase 5 | 创建时间: 2026-03-15

## 模块：Claude Code 代理 API (claude-code-proxy)

| # | 用例名称 | 层级 | 路径类型 | 前置条件 | 输入 | 预期输出 | 断言要点 |
|---|---------|------|---------|---------|------|---------|---------|
| 1 | mode=claude_code 路由正确 | unit | Happy Path | mock 实例服务 | askAgents(mode=claude_code) | 请求转发到实例服务 | 不走 MCP，调用 instance_service |
| 2 | mode=a2a 路由到旧引擎 | unit | Happy Path | mock MCP | askAgents(mode=a2a) | 请求走 MCP | 调用原有 MCP 逻辑 |
| 3 | SSE 格式转换正确 | unit | Happy Path | Claude Code 原始输出 | text/tool_use/done 事件 | 前端兼容的 SSE 格式 | event/name/result 字段正确映射 |
| 4 | 流式代理完整传输 | integration | Happy Path | 实例运行中 | askAgentsCheck(mode=claude_code) | SSE 流 | 收到 step 事件 + task_done |
| 5 | 用户停止任务 | integration | Happy Path | 任务执行中 | askAgentsUserStop | 任务中断 | 返回成功，后续无新 chunk |
| 6 | 对话历史保存 | integration | Happy Path | 完成一次对话 | 查询 MongoDB | 记录存在 | conv_id/question_id/mode 正确 |
| 7 | 未登录用户被拒 | unit | 错误路径 | 无 token | askAgents | 401 | code=30(session_expire) |
| 8 | 实例未启动时自动创建 | integration | Happy Path | 无运行实例 | askAgents(mode=claude_code) | 自动创建后返回 | mcp_task_id 非空 |

### 测试目的覆盖检查

| 测试目的 | 是否适用 | 用例编号 | 备注 |
|---------|---------|---------|------|
| 功能测试 | Yes | 1-6, 8 | |
| 性能测试 | N/A | — | 性能取决于 Claude CLI |
| 安全测试 | Yes | 7 | 认证检查 |
| 兼容性测试 | N/A | — | |
| 可用性测试 | N/A | — | |
