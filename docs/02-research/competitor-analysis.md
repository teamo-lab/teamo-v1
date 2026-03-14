# Teamo v1 竞品分析报告

> 调研日期：2026-03-14
> 竞品：Devin (devin.ai) / Claude.ai + Claude Code (Anthropic)

---

## 一、Devin (devin.ai) — AI 软件工程师

### 1.1 注册与上手流程

| 步骤 | 说明 |
|------|------|
| 注册方式 | SSO 登录（GitHub / Google Workspace），无独立邮箱注册 |
| 组织创建 | 注册后需创建组织 workspace |
| 仓库连接 | Settings → Integrations → GitHub，OAuth 授权，选择仓库并授予 Read/Write/PR 权限 |
| 环境配置 | 首次使用某仓库时走 onboarding flow，配置依赖安装、lint、测试等开发环境信息 |
| 首次任务引导 | 建议从测试仓库或非关键项目开始；可预设环境变量、框架偏好、编码规范 |
| 上手时间 | 约 1 小时完成完整 onboarding |

**定价体系（2026 年 3 月）：**

| 计划 | 价格 | ACU 额度 | 并发会话 | 关键差异 |
|------|------|----------|----------|----------|
| **Core** | $20 起（按量） | $2.25/ACU | 最多 10 个 | 基础功能，无 Advanced Mode |
| **Team** | $500/月 | 250 ACU 含内（超出 $2/ACU） | 无限 | 含 Advanced Mode |
| **Enterprise** | 定制 | 定制 | 无限 | VPC 部署、SAML/OIDC SSO、专属支持 |

> ACU（Agent Compute Unit）= VM 时间 + 模型推理 + 带宽的标准化度量。仅在 Devin 实际执行任务时消耗。

### 1.2 核心工作流

```
用户提交任务（聊天/Jira/Slack/API）
        ↓
Devin 分析代码库（秒级响应，展示相关文件 + 初步计划）
        ↓
Interactive Planning（用户可编辑/确认计划）
        ↓
自主执行（沙箱环境：编辑器 + 终端 + 浏览器）
        ↓
实时进度汇报 + 必要时请求用户介入
        ↓
创建分支 → 提交 PR → 可选自动 Review
```

**四 Agent 协作架构：**
- **Planner** — 任务拆解与策略
- **Coder** — 代码实现
- **Critic** — 代码审查
- **Browser** — 文档/网页研究

### 1.3 关键 UI/UX 模式

| 模式 | 描述 |
|------|------|
| **Agent-native Cloud IDE** | 每个 session 拥有独立的云端 IDE（编辑器 + 终端 + 沙箱浏览器） |
| **Interactive Planning** | 执行前展示计划，用户可编辑调整，避免无效迭代 |
| **Devin Search** | 代码库探索工具，支持 Deep Mode，引用具体代码行 |
| **Devin Wiki** | 自动生成仓库文档 + 架构图 |
| **Favicon 状态指示** | 浏览器标签页图标：🟢工作中 / 🟠等待用户 |
| **PWA 支持** | 可安装为桌面/移动端 Progressive Web App |
| **Thought Process 面板** | 展示推理过程，透明化决策 |
| **Session 列表** | 内联 PR 预览、消息摘要、状态指示器，支持按创建时间排序 |
| **Copy Context** | 一键生成 AI 摘要用于 session 交接 |
| **批量代码评论** | Review 时可累积多条评论后一次性提交 |

### 1.4 流式输出行为

- **主模式为异步**：提交任务后等待，不是实时逐 token 流式
- 通过 Dashboard URL 监控进度
- Webhook 回调通知状态变更（COMPLETED / NEEDS_INPUT）
- 实时汇报进展但有 **12-15 分钟响应延迟**（复杂任务场景）
- 浏览器 Favicon 颜色变化是最轻量的状态感知方式

### 1.5 实例模型

| 维度 | 说明 |
|------|------|
| 隔离性 | 每个 session 独立沙箱环境（终端 + 编辑器 + 浏览器） |
| 并行性 | 可同时启动多个 Devin 并行工作 |
| 生命周期 | 任务完成后 session 保留（可查看历史），会话列表可浏览 |
| 部署模式 | SaaS（默认）/ VPC 私有化部署（Enterprise） |
| 安全边界 | 沙箱内运行，无法直接访问生产数据库（除非用户显式提供凭据） |
| 仓库索引 | 每隔数小时自动重新索引 |

### 1.6 值得借鉴的设计亮点

1. **Interactive Planning 阶段** — 执行前让用户确认/编辑计划，减少无效计算消耗。对 Teamo 很有参考价值：用户提交任务后先展示计划，确认后再执行
2. **Favicon 状态指示器** — 极低成本的状态感知，用户不需要切换到 Devin 标签就能知道是否需要介入
3. **Session 列表设计** — 内联 PR 预览 + 消息摘要，一目了然。Teamo 的实例列表可以借鉴
4. **Copy Context（上下文导出）** — 会话交接场景非常实用
5. **Devin Wiki 自动文档生成** — 降低新仓库上手门槛
6. **桌面端 QA 测试** — Devin 可以运行应用 → 用桌面浏览器点击测试 → 发送录制视频给用户

### 1.7 痛点与局限

| 痛点 | 严重程度 | 说明 |
|------|----------|------|
| **成功率偏低** | 🔴 高 | 实测 20 个任务仅 3 个完全成功（15%）；复杂任务易陷入无限循环 |
| **响应延迟** | 🔴 高 | 12-15 分钟延迟，不够慢以放手去做别的事，不够快以实时交互 |
| **成本不可预测** | 🟡 中 | ACU 按量计费，用户启动任务时难以预估费用 |
| **模糊指令处理差** | 🟡 中 | 需要明确、具体的指令才能良好工作 |
| **质量不稳定** | 🟡 中 | 不同任务间表现差异大 |
| **第三方库冲突** | 🟡 中 | 处理依赖冲突和复杂配置时容易卡住 |

---

## 二、Claude.ai + Claude Code — Anthropic 官方方案

### 2.1 注册与上手流程

| 步骤 | 说明 |
|------|------|
| 注册方式 | 邮箱 / Google / Apple 账号 |
| 免费层 | 有免费版（有限额度），可即时开始聊天 |
| Claude Code 获取 | Pro ($20/月) 及以上计划均可使用终端版 Claude Code |
| Web 版 Claude Code | Pro/Max 用户可在 claude.ai/code 使用云端版本 |
| GitHub 连接 | 在 Web 版 Claude Code 中连接 GitHub 仓库 |
| 上手门槛 | 极低 — 注册即用，无需组织/workspace 创建 |

**定价体系（2026 年 3 月）：**

| 计划 | 价格 | Claude Code 权限 | 关键特性 |
|------|------|-------------------|----------|
| **Free** | $0 | ❌ 无 | 基础聊天，有限额度 |
| **Pro** | $20/月 | ✅ 终端版 + Web 版 | 标准额度 |
| **Max 5x** | $100/月 | ✅ 全功能 | 5 倍消息量 |
| **Max 20x** | $200/月 | ✅ 全功能 | 20 倍消息量 |
| **Team Standard** | $25/人/月 | ❌ 无 | 团队协作 |
| **Team Premium** | $150/人/月 | ✅ 含 Claude Code | 团队 + 编码 |
| **Enterprise** | 定制 | ✅ | SSO、审计、合规 |

### 2.2 核心工作流

**Web 版 Claude Code（异步模式）：**
```
用户在 claude.ai/code 指定 GitHub 仓库 + 输入任务描述
        ↓
Claude 在隔离沙箱容器中执行
        ↓
实时进度追踪（可在执行中追加指令，排队执行）
        ↓
用户可随时介入调整方向
        ↓
自动创建分支 → 生成 PR（含变更摘要）
```

**终端版 Claude Code（交互模式）：**
```
本地终端输入 `claude` 进入会话
        ↓
实时对话，逐步执行（读文件、写代码、运行命令）
        ↓
每个操作生成 Checkpoint（可随时回滚）
        ↓
子任务可 Ctrl+B 转后台并行执行
        ↓
/tasks 查看所有后台任务状态
```

**Teleport 功能：** Web 端执行结果可"传送"到本地终端，获取完整聊天记录和编辑后的文件。

### 2.3 关键 UI/UX 模式

| 模式 | 描述 |
|------|------|
| **双模态入口** | Web 版（异步、并行）+ 终端版（实时、交互）互补 |
| **Checkpoint 系统** | 每个操作自动创建检查点，可回滚代码 + 对话，跨 session 持久化 |
| **并行任务** | Web 版可跨多个仓库同时运行多个任务 |
| **Sidebar 导航** | Chats / Projects / Artifacts / Code 四个核心入口 |
| **权限对话框** | 工具使用前细粒度权限确认 |
| **子 Agent 后台化** | Ctrl+B 将子任务移至后台，主 session 继续工作 |
| **移动端支持** | iOS 应用内嵌早期 Claude Code 预览 |
| **Status Line（终端）** | 可定制底部状态栏：模型名、Git 分支、会话费用、上下文用量 |
| **VS Code 扩展** | 原生集成 VS Code / Cursor |

### 2.4 流式输出行为

| 维度 | Web 版 | 终端版 |
|------|--------|--------|
| 输出模式 | 异步 + 实时进度追踪 | 逐 token 流式输出 |
| 交互性 | 执行中可追加排队指令 | 实时对话，即时响应 |
| 延迟 | 复杂任务数分钟（"churned away for a few minutes"） | 秒级响应 |
| 中间状态 | 进度指示器 | 终端实时输出命令结果 |

### 2.5 实例模型

| 维度 | 说明 |
|------|------|
| 隔离性 | 每个 Web 任务在独立隔离沙箱容器中运行 |
| 安全 | 网络和文件系统限制；Git 操作经安全代理路由 |
| 并行性 | 可同时运行多个任务（跨不同仓库） |
| 额度共享 | 云端 session 与所有 Claude Code 使用共享速率限制 |
| 网络策略 | 管理员可配置自定义网络策略（如允许 npm 但限制其他域名） |
| 容器技术 | CLI 包装在容器中；使用 Bubblewrap (Linux) / seatbelt (macOS) 沙箱化 |
| Checkpoint | 每个操作产生检查点，跨 session 持久化 |

### 2.6 值得借鉴的设计亮点

1. **Checkpoint + 回滚** — 每个操作自动快照，可回滚代码和/或对话到任意历史点。这对用户安全感极为重要，Teamo 必须实现类似机制
2. **双模态互补** — Web 版做异步并行，终端版做实时交互。两种场景都覆盖
3. **Teleport** — Web 端结果无缝迁移到本地环境，打通"云端执行 → 本地继续"的工作流
4. **极低上手门槛** — 注册即用，无需创建组织/workspace，降低初次转化摩擦
5. **子 Agent 后台化 (Ctrl+B)** — 长耗时任务不阻塞主工作流
6. **自定义 Status Line** — 终端用户可按需定制信息展示（模型、费用、上下文窗口使用率）
7. **网络隔离 + 自定义策略** — 安全与灵活性平衡

### 2.7 痛点与局限

| 痛点 | 严重程度 | 说明 |
|------|----------|------|
| **速率限制共享** | 🔴 高 | 云端 session 与 CLI / 聊天共享额度，重度用户容易撞限 |
| **成本不透明** | 🟡 中 | Pro $20/月看似便宜但 Max 层 $100-200/月，Web 版消耗速率不明确 |
| **Web 版控制力弱** | 🟡 中 | 比终端版缺少逐步审批的控制力 |
| **"Trusted Network" 安全疑虑** | 🟡 中 | 默认网络白名单存在数据外泄风险 |
| **移动端不成熟** | 🟡 中 | iOS 预览版体验初步 |
| **无 VPC 私有化方案** | 🔴 高（对企业用户）| 代码必须经过 Anthropic 云端 |

---

## 三、竞品对比总结

| 维度 | Devin | Claude Code (Web) | **Teamo v1 机会** |
|------|-------|--------------------|--------------------|
| **定位** | 自主 AI 工程师（异步委托） | 开发者 AI 助手（交互+异步） | 专属云端 Claude Code 实例 |
| **最低价格** | $20 起（按量） | $20/月（Pro 包含） | 需定价有竞争力 |
| **上手门槛** | 中等（~1 小时 onboarding） | 低（注册即用） | 应追求极低门槛 |
| **实例隔离** | ✅ 独立沙箱 per session | ✅ 独立容器 per task | ✅ 专属实例（核心差异化） |
| **并行能力** | Core 10 / Team 无限 | 多任务并行 | 按实例粒度并行 |
| **流式输出** | ❌ 异步为主，延迟大 | 🔶 Web 异步 / CLI 实时 | 必须支持实时流式 |
| **Checkpoint/回滚** | ❌ 无 | ✅ 完整检查点系统 | 应实现 |
| **计划确认** | ✅ Interactive Planning | ❌ 直接执行 | 可选实现 |
| **VPC/自部署** | ✅ Enterprise | ❌ 无 | 潜在方向 |
| **GitHub 集成** | ✅ 深度（PR + Review） | ✅ 自动创建 PR | 必须支持 |

### Teamo v1 的差异化机会

1. **"专属实例"心智** — Devin 是"雇一个 AI 工程师"，Claude Code 是"用工具"，Teamo 可以是"拥有自己的云端开发环境 + AI 驻场"
2. **实时流式输出** — Devin 的 12-15 分钟延迟是重大痛点。Teamo 应提供真正的实时终端流式输出
3. **透明定价** — 两个竞品的实际成本都不够透明。Teamo 应提供可预测的定价（按实例时长或固定月费）
4. **Checkpoint 必须有** — Claude Code 的检查点系统是用户安全感的基础，Teamo 需要实现
5. **执行前计划确认** — 借鉴 Devin 的 Interactive Planning，在消耗算力前让用户确认方向
6. **中国网络优化** — 竞品均为海外服务，Teamo 在国内网络环境下有天然优势

---

## Sources

### Devin
- [Devin Pricing](https://devin.ai/pricing/)
- [Devin 2.0 发布 (Cognition)](https://cognition.ai/blog/devin-2)
- [Devin AI Guide 2026](https://aitoolsdevpro.com/ai-tools/devin-guide/)
- [Devin Review 2026](https://ai-coding-flow.com/blog/devin-review-2026/)
- [Devin AI Review: The Good, Bad & Costly Truth](https://trickle.so/blog/devin-ai-review)
- [Devin Recent Updates](https://docs.devin.ai/release-notes/overview)
- [Devin 2.0 价格下调 (VentureBeat)](https://venturebeat.com/programming-development/devin-2-0-is-here-cognition-slashes-price-of-ai-software-engineer-to-20-per-month-from-500)
- [Devin 年度绩效回顾 2025](https://cognition.ai/blog/devin-annual-performance-review-2025)
- [Devin GitHub Integration Docs](https://docs.devin.ai/integrations/gh)

### Claude Code
- [Claude Code on the Web (Anthropic)](https://claude.com/blog/claude-code-on-the-web)
- [Claude Code for Web 分析 (Simon Willison)](https://simonwillison.net/2025/Oct/20/claude-code-for-web/)
- [Claude Code Async Workflows](https://claudefa.st/blog/guide/agents/async-workflows)
- [Claude Pricing](https://claude.com/pricing)
- [Claude Code Pricing 2026](https://claudelog.com/claude-code-pricing/)
- [Claude AI Pricing 2026 Guide](https://www.glbgpt.com/hub/claude-ai-pricing-2026-the-ultimate-guide-to-plans-api-costs-and-limits/)
- [Anthropic 2026 产品发布汇总](https://fazal-sec.medium.com/anthropics-explosive-start-to-2026-everything-claude-has-launched-and-why-it-s-shaking-up-the-668788c2c9de)
