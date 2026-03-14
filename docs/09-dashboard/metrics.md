# Teamo v1 Dashboard 指标定义

> Phase 9 | 创建时间: 2026-03-15

## 核心指标

| 指标 | 来源 | 计算方式 | 告警阈值 |
|------|------|---------|---------|
| 活跃实例数 | GET /health (instance-manager) | active_instances | < 0 异常 |
| 实例创建成功率 | POST /api/instance/create 响应 | 200 / total | < 95% |
| 平均响应延迟 | POST /api/instance/prompt SSE 首字节 | p95 latency | > 10s |
| 每日活跃用户 | Claude Code 模式 askAgents 去重 user_id | count(distinct user_id) | — |
| Credits 消耗 | daily_billing_task 日志 | sum(deducted) | — |
| 停机用户数 | credits=0 触发 stop | count | — |

## 健康检查端点

| 服务 | 端点 | 预期 |
|------|------|------|
| Instance Manager | http://127.0.0.1:8902/health | {"status":"ok"} |
| Claude Code Proxy | http://127.0.0.1:8901/api/engine/instanceStatus | {"code":0} |

## 日志采集

- 两个服务均用 systemd journal，可通过 `journalctl -u <service>` 查看
- 关键日志关键词：`ERROR`, `timeout`, `crashed`, `restarting`
