# Claude Code 实例管理服务 PRD

> Phase 4 | 模块: instance-manager | 创建时间: 2026-03-15

## 模块概述

管理用户专属 Claude Code 云端实例的创建、销毁、状态查询和生命周期。基于 deploy-claude-cloud 二次开发。

## 用户故事

- 作为用户，我希望首次发送任务时自动创建专属实例，以便无需手动配置
- 作为系统，我需要在用户 credits 为 0 时自动关机，以便控制成本
- 作为用户，我希望看到实例状态（运行中/创建中/已关机），以便了解当前状态

## 功能清单

| # | 功能 | 优先级 | MVP | 描述 |
|---|------|--------|-----|------|
| 1 | 创建实例 | P0 | Yes | 首次使用时自动创建 Claude Code 进程 |
| 2 | 发送 Prompt | P0 | Yes | 向用户实例发送任意 prompt，流式返回结果 |
| 3 | 查询状态 | P0 | Yes | 查询实例运行状态 |
| 4 | 销毁实例 | P0 | Yes | credits 为 0 时自动销毁 |
| 5 | 健康检查 | P1 | Yes | 定期检查实例是否存活 |
| 6 | 实例重启 | P1 | Yes | 实例异常时自动重启 |

## API 设计

### POST /api/instance/prompt
向用户实例发送 prompt，流式返回结果。
```
Request:
{
  "user_id": "string",
  "prompt": "string",
  "session_id": "string (optional)",
  "cwd": "string (optional)"
}

Response: SSE Stream
data: {"type": "text", "content": "思考中..."}
data: {"type": "tool_use", "tool": "Read", "input": {"file_path": "/app/main.py"}}
data: {"type": "tool_result", "content": "文件内容..."}
data: {"type": "text", "content": "我来修改这个文件..."}
data: {"type": "done", "session_id": "xxx"}
```

### GET /api/instance/status/{user_id}
查询实例状态。
```
Response:
{
  "status": "running|creating|stopped|error",
  "created_at": "ISO timestamp",
  "uptime_seconds": 86400,
  "session_id": "current session"
}
```

### POST /api/instance/create
创建实例（内部调用，由 prompt 接口自动触发）。

### POST /api/instance/destroy/{user_id}
销毁实例。

## 数据模型

```
ClaudeInstance:
    user_id: str           # 用户 ID（主键）
    status: str            # running | creating | stopped | error
    process_pid: int       # Claude Code 进程 PID
    home_dir: str          # 实例专用 HOME 目录
    created_at: datetime
    last_active_at: datetime
    session_id: str        # 当前会话 ID
```

## 技术实现

- 基于 asyncio.create_subprocess_exec() 异步调用 Claude CLI
- 每用户独立 HOME 目录（/opt/teamo/instances/{user_id}/）
- Claude CLI 使用 -p 参数非交互模式 + --output-format json
- 流式输出通过 StreamingResponse SSE 返回
- 实例状态存储在 Redis（快速查询）+ MongoDB（持久化）

## 业务规则

- 首次发送 prompt 时自动创建实例，无需用户手动操作
- 实例创建超时 120 秒，超时返回错误
- Credits 为 0 时，定时任务检查并销毁实例
- 实例异常（进程崩溃）时自动重启，最多重试 3 次
- 单用户只能有 1 个活跃实例
