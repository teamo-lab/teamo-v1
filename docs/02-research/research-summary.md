# Teamo v1 调研总结

> Phase 2 | 创建时间: 2026-03-14 | 状态: 完成

## 一页总结

### 市场定位

AI 编码 Agent 市场正从 "辅助编码" 向 "自主开发" 快速转变。73% 开发者已日常使用 AI 工具，但满意度仅 60% 且在下降。**用户已经知道 AI 编码能做什么，但现有产品的体验远未满足期望。**

### 关键发现

1. **市场空白确认**：纯 Web + 用户专属 Claude Code 实例的组合，目前没有直接竞品
   - Cursor/Windsurf = 桌面 IDE（非 Web）
   - Devin = Web 但黑盒 Agent（非 Claude Code）
   - ChatGPT = Web 但无持久环境（沙箱）
   - GitHub Agent HQ = 刚起步，面向 Pro+ 用户

2. **用户 Top 5 痛点与 Teamo 的回应**：
   | 痛点 | 频率 | Teamo v1 如何解决 |
   |------|------|------------------|
   | 跨会话记忆丢失 | #1 | 用户专属持久实例，天然保持项目上下文 |
   | 定价不透明 | #2 | 28 credits/天，按天计费清晰可预测 |
   | 无 Web 界面 | #3 | 聊天式 Web UI，零配置即用 |
   | Agent 行为不可控 | #4 | Claude Code 透明每一步，CLAUDE.md 精确控制 |
   | 代码质量不稳定 | #5 | Claude Opus 4.6 代码质量业界领先 |

3. **竞争风险**：
   - Anthropic 自己可能推出 Claude Code Web 版
   - Cursor Cloud Agent 向 Web 方向演进
   - GitHub Agent HQ 已整合 Claude Code

4. **技术趋势利好**：
   - MCP 协议成标准 → Teamo 可复用 Claude Code 生态
   - Background Agents 成标配 → 用户专属实例天然支持
   - Skills 系统 → 可预装 Skills 降低用户上手门槛

### 对产品设计的 5 条核心建议

1. **MVP 聚焦核心链路**：发送任务 → Claude Code 执行 → 流式展示 → 对话历史。不要在 MVP 阶段做多 Agent 协作
2. **透明度是差异化武器**：展示每一步操作（文件读写、命令执行、思考过程），不做黑盒
3. **定价简单透明**：28 credits/天的模型比 ACU、Credit Pack 更有吸引力
4. **预配置降低门槛**：为用户实例预装 CLAUDE.md + 常用 Skills，开箱即用
5. **速度优先于功能**：用户更在意 "能不能用"，而不是 "功能多不多"。先上线，再迭代

### 建议定价区间
- 个人版：$25-35/月（远低于 Devin $500，略高于 Cursor $20 以反映专属实例价值）
- 混合模式：基础月费含 N 天实例运行 + 超出按天计费
