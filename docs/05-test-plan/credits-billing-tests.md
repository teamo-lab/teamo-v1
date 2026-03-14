# 测试计划：Credits 计费系统

> Phase 5 | 创建时间: 2026-03-15

## 模块：Credits 计费 (credits-billing)

| # | 用例名称 | 层级 | 路径类型 | 前置条件 | 输入 | 预期输出 | 断言要点 |
|---|---------|------|---------|---------|------|---------|---------|
| 1 | 正常每日扣费 | unit | Happy Path | 用户有 100 credits, 实例运行中 | daily_billing_task() | credits=72 | 扣除 28, 实例仍 running |
| 2 | 余额不足停机 | unit | Happy Path | 用户有 20 credits, 实例运行中 | daily_billing_task() | credits=20, 实例 stopped | 不扣费, 实例被停止 |
| 3 | 余额恰好 28 | unit | 边界值 | 用户有 28 credits | daily_billing_task() | credits=0, 实例 running | 扣完后实例仍运行到下一周期 |
| 4 | 余额为 0 已停机 | unit | 边界值 | credits=0, 实例已 stopped | daily_billing_task() | 无变化 | 不重复停机 |
| 5 | 扣费优先级正确 | unit | Happy Path | free=10, vip=10, extend=50 | 扣 28 | free=0, vip=0, extend=42 | 按优先级扣除 |
| 6 | 查询余额信息 | unit | Happy Path | credits=156 | GET /creditsInfo | 正确余额信息 | total=156, daily=28, days=5 |
| 7 | 低余额警告 | unit | Happy Path | credits=56 (2 天) | GET /creditsInfo | 包含 warning | warning 非空, 包含"不足" |
| 8 | 充值后恢复实例 | integration | Happy Path | credits=0+已停机 → 充值 100 | 触发恢复检查 | 实例重启 | status=running |

### 测试目的覆盖检查

| 测试目的 | 是否适用 | 用例编号 | 备注 |
|---------|---------|---------|------|
| 功能测试 | Yes | 1-8 | |
| 性能测试 | N/A | — | |
| 安全测试 | N/A | — | 计费逻辑内部调用 |
| 兼容性测试 | N/A | — | |
| 可用性测试 | N/A | — | |
