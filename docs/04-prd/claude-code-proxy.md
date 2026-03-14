# Claude Code 代理 API PRD

> Phase 4 | 模块: claude-code-proxy | 创建时间: 2026-03-15

## 模块概述

wowchat-backend 新增模块，接收前端请求，转发到用户专属 Claude Code 实例，流式返回结果。作为前端和实例管理服务之间的桥梁。

## 用户故事

- 作为用户，我希望在聊天框输入任务后，Claude Code 实时执行并流式展示过程
- 作为用户，我希望可以随时停止正在执行的任务
- 作为用户，我希望切换到 Research 模式时，请求走老引擎

## 功能清单

| # | 功能 | 优先级 | MVP | 描述 |
|---|------|--------|-----|------|
| 1 | 发起 Claude Code 任务 | P0 | Yes | 接收前端请求，转发到实例管理服务 |
| 2 | SSE 流式返回 | P0 | Yes | 将实例的流式输出转发到前端 |
| 3 | 停止任务 | P0 | Yes | 用户点击停止时，中断实例执行 |
| 4 | 模式路由 | P0 | Yes | mode=claude_code 走新引擎，其他走老引擎 |
| 5 | 对话历史保存 | P1 | Yes | 将 Claude Code 的输入输出保存到 MongoDB |
| 6 | Credits 扣费 | P1 | Yes | 每日定时扣除运行实例的 credits |

## API 设计（wowchat-backend 新增端点）

### POST /api/engine/askAgents（扩展现有接口）

在现有 askAgents 接口中增加 mode 判断：
```python
if mode == 'claude_code':
    # 转发到 Claude Code 实例管理服务
    response = await instance_service.prompt(user_id, query, session_group_id)
    return {"mcp_task_id": response.task_id}
else:
    # 走原有 MCP 引擎（Research 模式）
    ...
```

### POST /api/engine/askAgentsCheck（扩展现有接口）

```python
if mode == 'claude_code':
    # 从 Claude Code 实例读取 SSE 流
    async def stream():
        async for chunk in instance_service.stream(task_id):
            yield format_as_existing_sse(chunk)
    return StreamingResponse(stream())
else:
    # 走原有 MCP 轮询逻辑
    ...
```

### POST /api/engine/askAgentsUserStop（扩展现有接口）

```python
if mode == 'claude_code':
    await instance_service.abort(user_id, task_id)
else:
    # 走原有停止逻辑
    ...
```

### GET /api/engine/instanceStatus
```json
Response:
{
  "code": 0,
  "result": {
    "status": "running",
    "credits_remaining": 156,
    "daily_cost": 28,
    "estimated_days": 5
  }
}
```

## SSE 事件格式（兼容现有前端）

将 Claude Code 的输出映射为现有前端能理解的 SSE 格式：

```python
# Claude Code 原始输出 → 前端 SSE 格式

# 思考过程
{"type": "thinking", "content": "..."}
→ {"event": "step", "name": "think_chunk", "result": {"message": "..."}}

# 文本输出
{"type": "text", "content": "..."}
→ {"event": "step", "name": "answer_chunk", "result": {"message": "..."}}

# 工具调用
{"type": "tool_use", "tool": "Read", ...}
→ {"event": "step", "name": "tool_call", "result": {"tool": "Read", ...}}

# 工具结果
{"type": "tool_result", "content": "..."}
→ {"event": "step", "name": "tool_result", "result": {"output": "..."}}

# 完成
{"type": "done"}
→ {"event": "task_done"}
```

## 数据模型

```python
# 复用现有 MongoDB 集合，增加标记
class ClaudeCodeConversation:
    conv_id: str
    question_id: str
    session_group_id: str
    username: str
    role: str              # 'user' | 'claude_code'
    query: str             # 用户输入
    response: str          # Claude Code 完整输出
    steps: List[dict]      # 步骤列表（与前端 steps 格式一致）
    mode: str = 'claude_code'
    battery_cost: float    # 0（按天计费，不按次）
    request_time: datetime
```

## 业务规则

- mode='claude_code' 的请求不走 MCP 服务，直接请求实例管理服务
- 前端 SSE 格式必须与现有格式兼容（复用 MessageBubble 组件）
- 对话历史与 Research 模式共享同一个 session_group_id 下
- Credits 按天扣费（28 credits/天），不按单次请求计费
