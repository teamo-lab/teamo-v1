# 测试计划：实例管理服务

> Phase 5 | 创建时间: 2026-03-15

## 模块：实例管理服务 (instance-manager)

| # | 用例名称 | 层级 | 路径类型 | 前置条件 | 输入 | 预期输出 | 断言要点 |
|---|---------|------|---------|---------|------|---------|---------|
| 1 | 创建实例成功 | unit | Happy Path | 无运行实例 | user_id="test1" | Instance(status=running) | status="running", pid>0, home_dir 存在 |
| 2 | 发送 prompt 流式返回 | integration | Happy Path | 实例运行中 | prompt="say hello" | SSE 流包含 text 事件 | 至少 1 个 type=text chunk, 最终有 type=done |
| 3 | 查询实例状态 | unit | Happy Path | 实例运行中 | user_id="test1" | status=running | status 字段精确匹配 |
| 4 | 销毁实例 | unit | Happy Path | 实例运行中 | user_id="test1" | status=stopped | 进程已终止, home_dir 保留 |
| 5 | 重复创建同用户实例 | unit | 边界值 | 已有运行实例 | user_id="test1" | 复用现有实例 | 不创建新进程，返回现有实例 |
| 6 | 不存在用户查状态 | unit | 错误路径 | 无此用户实例 | user_id="nonexist" | status=stopped | status="stopped" |
| 7 | prompt 超时处理 | integration | 错误路径 | 实例运行中 | prompt 导致超时 | 超时错误 | 返回 timeout error, 实例仍存活 |
| 8 | 实例崩溃后自动重启 | integration | 降级 | 手动 kill 进程 | 发送新 prompt | 自动重启并响应 | 新 pid != 旧 pid, 响应正常 |
| 9 | 健康检查接口 | unit | Happy Path | 服务运行中 | GET /health | 200 + status | status="ok" |

### 测试目的覆盖检查

| 测试目的 | 是否适用 | 用例编号 | 备注 |
|---------|---------|---------|------|
| 功能测试 | Yes | 1-6, 9 | |
| 性能测试 | Yes | — | 实例创建 < 120s（部署后验证） |
| 安全测试 | N/A | — | 内部服务，不直接暴露 |
| 兼容性测试 | N/A | — | 纯后端 |
| 可用性测试 | N/A | — | 纯后端 |
