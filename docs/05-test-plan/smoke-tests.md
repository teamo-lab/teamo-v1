# 冒烟测试清单

> Phase 5 | 创建时间: 2026-03-15 | 用途: 部署后快速验证

## 冒烟测试（部署后 5 分钟内完成）

| # | 检查项 | 方法 | 预期 | 阻断级别 |
|---|--------|------|------|----------|
| 1 | 实例管理服务健康 | GET /health | 200 + ok | 阻断 |
| 2 | wowchat-backend 健康 | GET /api/health | 200 | 阻断 |
| 3 | 前端页面加载 | 浏览器打开首页 | 页面渲染 < 3s | 阻断 |
| 4 | 登录功能 | POST /api/oauth2/login | 返回 token | 阻断 |
| 5 | Claude Code 模式发消息 | POST /api/engine/askAgents(mode=claude_code) | 返回 mcp_task_id | 阻断 |
| 6 | SSE 流式响应 | POST /api/engine/askAgentsCheck | 收到 SSE 事件 | 阻断 |
| 7 | Research 模式发消息 | POST /api/engine/askAgents(mode=a2a) | 返回 mcp_task_id | 非阻断 |
| 8 | Credits 余额查询 | GET /api/engine/creditsInfo | 返回余额信息 | 非阻断 |
| 9 | 实例状态查询 | GET /api/instance/status/{user_id} | 返回状态 | 非阻断 |
