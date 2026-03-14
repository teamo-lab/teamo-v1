# Teamo v1 竞品分析报告

> 调研日期：2026-03-14
> 产品定位：为每位用户提供专属云端 Claude Code 实例，通过类聊天 Web UI 进行交互

---

## 一、直接竞品

### 1. Cursor (cursor.com)

**产品形态**：基于 VS Code 的 AI 代码编辑器（桌面应用），内置 Agent 模式

**核心功能**：
- Agent 模式：可自主分析代码、跨文件编辑、运行命令、修复错误
- Tab 补全：智能代码预测与补全
- 多模型支持：OpenAI GPT、Claude、Gemini 系列模型可选
- Cloud Agent：云端运行 Agent 任务（不占用本地资源）
- MCP 支持：可接入外部工具和服务
- BugBot：自动 PR 代码审查

**定价模型**：
| 计划 | 价格 | 说明 |
|------|------|------|
| Hobby（免费） | $0 | 有限 Agent 请求和补全次数 |
| Pro | $20/月 | 扩展 Agent 用量，前沿模型访问，MCP/Skills/Hooks |
| Pro+ | $60/月 | 3x 用量（所有模型） |
| Ultra | $200/月 | 20x 用量，优先体验新功能 |
| Teams | $40/人/月 | 共享聊天/规则，团队管理，SSO |
| Enterprise | 定制 | 池化用量，审计日志，SCIM |

**关键优势**：
- 编辑器体验成熟，VS Code 生态兼容性好，开发者上手成本低
- 多模型支持灵活，用户可按场景切换模型
- Cloud Agent 能力正在补齐「云端运行」短板

**关键劣势**：
- 核心是桌面 IDE，非纯 Web 体验；Cloud Agent 是附加功能而非核心架构
- Agent 能力受限于编辑器沙箱，无法像独立实例那样完全控制文件系统和环境
- 高用量场景（Ultra $200/月）价格昂贵

**Agent 概念**：Agent 是编辑器内的一个模式，在用户的项目上下文中执行多步操作。Cloud Agent 可在云端执行，但本质上仍依附于 IDE 工作流。

---

### 2. Windsurf (windsurf.com，原 Codeium)

**产品形态**：自称「首个 Agentic IDE」，桌面代码编辑器 + Cascade Agent

**核心功能**：
- Cascade Agent：深度上下文感知的 AI 流式协作，结合 Copilot 交互性和 Agent 自主性
- SWE-1.5：自研 Agent 模型，优化编码任务
- Windsurf Previews：IDE 内实时网页预览，可直接对 UI 元素操作
- MCP 支持：通过 Model Context Protocol 接入自定义工具
- Tab to Jump：智能光标位置预测
- 主流模型全支持（First-class support for every major model provider）

**定价模型**：
| 计划 | 价格 | 信用点数 |
|------|------|----------|
| Free | $0 | 25 credits/月 |
| Pro | $15/月 | 500 credits/月，超出 $10/250 credits |
| Teams | $30/人/月 | 500 credits/人/月 + Fast Context |
| Enterprise (<=200人) | 定制 | 1,000 credits/人/月 |
| Enterprise (>200人) | 定制 | 无限 credits |

**关键优势**：
- 起步价最低（Pro $15/月），对个人开发者友好
- Cascade 的实时行为感知能力独特——AI 持续监控开发者操作并自动调整上下文
- 自研 SWE-1.5 模型针对代码任务优化

**关键劣势**：
- 同样是桌面 IDE，没有纯 Web 访问方式
- 信用点制度不透明，用户难以预估实际消耗
- 品牌认知度不如 Cursor，从 Codeium 更名后仍在建立市场影响力

**Agent 概念**：Cascade 作为「AI Flow」在编辑器中运行，融合了 Copilot 的交互性和 Agent 的自主性，但仍然绑定桌面 IDE 环境。

---

### 3. Devin (devin.ai)

**产品形态**：自主 AI 软件工程师，Web 界面 + Slack/Teams 集成，最接近 Teamo 的竞品

**核心功能**：
- 全自主开发：从接收 ticket 到提交 PR 的完整流程
- Devin IDE：内置 Web 端开发环境
- 多工具集成：GitHub、Linear、Slack、Teams、Jira、AWS、Stripe 等 20+ 工具
- MCP 服务器支持
- Ask Devin：对话式代码问答
- Wiki：自动生成项目知识库
- 学习能力：从代码模式和项目惯例中持续学习

**定价模型**：
| 计划 | 价格 | 说明 |
|------|------|------|
| Core | $20 起（按量） | $2.25/ACU，最多 10 并发 session |
| Team | $500/月 | 含 250 ACU（$2.00/ACU），无限并发 |
| Enterprise | 定制 | 无限 ACU，VPC 部署，SAML/SSO |

> ACU（Agent Compute Unit）= VM 时间 + 模型推理 + 带宽的标准化度量

**关键优势**：
- 真正的自主 Agent——可以独立完成从 ticket 到 PR 的全流程，不需要人类逐步指导
- Web 原生 + Slack/Teams 集成，非桌面 IDE 依赖
- 案例数据亮眼：Nubank 迁移任务实现 8-12x 效率提升、20x 成本节约

**关键劣势**：
- 定价偏高，Team 计划 $500/月 起，ACU 消耗不可预测
- 黑盒模型——不基于 Claude Code 或其他公开模型，用户无法选择底层 AI
- 更适合「委托任务」场景，交互式编码体验不如 IDE 类产品

**Agent 概念**：Devin 本身就是一个完整的 AI Agent，拥有独立的执行环境、浏览器、终端。与 Teamo 最相似，但 Teamo 的差异化在于基于 Claude Code 且用户对实例有完全控制权。

---

### 4. Augment Code (augmentcode.com)

**产品形态**：自称「软件 Agent 公司」，IDE 插件 + CLI + 远程 Agent

**核心功能**：
- Context Engine（核心卖点）：从 4,456+ 来源中筛选相关上下文，理解整个技术栈
- 多 Agent 工作流：IDE Agent、Intent（多 Agent 协调）、Code Review、CLI、Slack
- Remote Agent：分布式远程 Agent 执行
- 支持 VS Code、JetBrains、CLI
- MCP 和原生工具支持

**定价模型**：
| 计划 | 价格 | Credits |
|------|------|---------|
| Indie | $20/月 | 40,000/月 |
| Standard | $60/人/月 | 130,000/月 |
| Max | $200/人/月 | 450,000/月 |
| Enterprise | 定制 | 自定义 |

**关键优势**：
- Context Engine 技术领先——SWE-Bench Pro 排行榜 51.80% 居首（超过 Cursor 和 Claude Code）
- 多入口（IDE/CLI/Slack/Remote），覆盖开发者各种工作场景
- 在企业客户中有强背书（MongoDB、Spotify、Snyk）

**关键劣势**：
- 没有独立 Web 界面，仍依赖 IDE 或 CLI
- Credit 制度复杂，团队池化但过期规则增加管理成本
- 品牌知名度低于 Cursor/Copilot，市场教育成本高

**Agent 概念**：通过 Intent 功能实现多 Agent 协调工作，每个 Agent 有隔离环境和 living specification。Remote Agent 接近云端执行，但核心仍是 IDE 辅助工具。

---

### 5. GitHub Copilot Workspace

**产品形态**：GitHub 原生的 Agent 工作空间（Web 端），可从 Issue 直接生成代码变更

**核心功能**：
- 三大 Agent：Plan Agent（意图捕获）、Brainstorm Agent（方案讨论）、Repair Agent（自动修复）
- Specification 驱动：AI 分析代码库生成「当前状态」和「目标状态」规格说明
- 集成终端和端口转发，支持验证测试
- 一键创建 PR，支持 Codespaces 完整 IDE 能力
- 基于 GPT-4o

**定价模型**：
| 计划 | 价格 | 说明 |
|------|------|------|
| Free | $0 | 2,000 补全 + 50 聊天/月 |
| Pro | $10/月 | 无限补全，多模型访问，Coding Agent |
| Enterprise | $39/人/月 | 高级模型（含 Claude Opus 4.6），治理控制 |

> 注意：Copilot Workspace 技术预览已于 2025-05-30 结束，功能正在整合进 Copilot Agent Mode。

**关键优势**：
- GitHub 原生集成，拥有最大的开发者分发渠道
- 从 Issue 到 PR 的工作流最自然，贴合现有开发习惯
- 价格最低（Pro $10/月），且有免费层

**关键劣势**：
- Workspace 已结束预览，后续形态不确定；Agent Mode 仍在演进中
- 绑定 GitHub 生态，对使用其他代码托管的团队不友好
- 缺乏独立执行环境，复杂任务能力弱于 Devin 和 Claude Code

**Agent 概念**：通过 Specification → Plan → Execute 的结构化流程驱动 Agent，强调人类在 Spec 和 Plan 阶段的可控性。

---

## 二、间接竞品

### 1. ChatGPT with Code Interpreter（OpenAI）

**产品形态**：通用 AI 对话 + 沙箱代码执行环境

**核心功能**：
- Code Interpreter / Advanced Data Analysis：在沙箱中运行 Python 代码
- 文件上传与处理（CSV、Excel、图片等）
- 数据分析与可视化
- Canvas：类似文档/代码编辑器的交互界面

**定价模型**：
| 计划 | 价格 | 说明 |
|------|------|------|
| Free | $0 | 有限对话次数 |
| Plus | $20/月 | GPT-4o、Code Interpreter、高级语音 |
| Pro | $200/月 | 无限访问、o1 Pro、扩展思考 |
| Team | $25-30/人/月 | 团队管理 + 更高用量 |

**关键优势**：
- 用户基数最大，品牌认知度最高
- 纯 Web 体验，零配置即可运行代码
- 多模态能力强（图像、语音、文件处理）

**关键劣势**：
- 沙箱环境严格隔离，无法访问用户真实项目文件系统
- 不是为软件工程设计的——无 Git、无持久环境、无项目上下文
- 只支持 Python 执行，不支持完整开发工作流

**Agent 概念**：本质是对话式 AI + 一次性代码沙箱，不具备持久 Agent 环境和项目级上下文管理能力。

---

### 2. Replit Agent (replit.com)

**产品形态**：云端 IDE + AI Agent，从对话到部署的全栈平台

**核心功能**：
- Replit Agent：通过自然语言描述需求，AI 自动搭建项目、写代码、配置环境
- 即时部署：一键将项目部署到 Replit 托管环境
- 在线 IDE：全功能 Web IDE，支持多语言
- 协作功能：实时多人协作编辑
- Ghostwriter：AI 代码补全和聊天

**定价模型**：
| 计划 | 价格 | 说明 |
|------|------|------|
| Free | $0 | 基础功能 |
| Replit Core | ~$20-25/月 | Agent 功能、更多计算资源、私有项目 |
| Teams | 按人计费 | 团队协作和管理 |

**关键优势**：
- 从编码到部署一体化，用户不需要任何本地环境
- 纯 Web 体验，对非专业开发者（产品经理、设计师）极友好
- 内置托管和部署，减少 DevOps 负担

**关键劣势**：
- 面向快速原型和小项目，不适合大型企业级代码库
- 计算资源受限于 Replit 容器，性能和灵活性不如独立实例
- Agent 的代码质量和复杂任务处理能力不如专业 AI 编码工具

**Agent 概念**：Replit Agent 是一个全栈自主 Agent，可以从零开始搭建项目，但更偏向快速原型开发而非企业级软件工程。

---

## 三、功能对比矩阵

| 维度 | Teamo v1 | Cursor | Windsurf | Devin | Augment Code | Copilot | ChatGPT Code | Replit Agent |
|------|----------|--------|----------|-------|--------------|---------|--------------|--------------|
| **专属实例/用户** | Y | N | N | Y | N | N | N | 部分 |
| **完整 Claude Code 能力** | Y | 部分 | N | N | N | 部分 | N | N |
| **纯 Web 界面** | Y | N (桌面) | N (桌面) | Y | N (IDE插件) | 部分 | Y | Y |
| **实时流式输出** | Y | Y | Y | Y | Y | Y | Y | Y |
| **文件系统访问** | Y (完整) | Y (项目级) | Y (项目级) | Y (沙箱) | Y (项目级) | Y (项目级) | N (沙箱) | Y (容器) |
| **工具使用 / MCP** | Y | Y | Y | Y | Y | Y | N | N |
| **多模型支持** | N (Claude) | Y | Y | N (自研) | Y | Y | N (GPT) | 部分 |
| **协作功能** | 计划中 | Y (Teams) | Y (Teams) | Y (Slack) | Y (多入口) | Y (Spaces) | N | Y |
| **定价模型** | TBD | $0-200/月 | $0-30/月 | $20-500+/月 | $20-200/月 | $0-39/月 | $0-200/月 | $0-25/月 |

---

## 四、Teamo v1 竞争定位分析

### 独特价值主张（与竞品的关键差异）

1. **专属云端 Claude Code 实例**：市场上唯一提供「每用户一个完整 Claude Code 运行时」的产品。Cursor/Windsurf 是桌面 IDE，Devin 是黑盒 Agent，ChatGPT/Replit 是受限沙箱。Teamo 让用户拥有真正的云端开发环境 + Claude Code 全部能力（工具调用、MCP、文件系统、长上下文）。

2. **纯 Web + 聊天式交互**：无需下载安装任何客户端。与 Cursor/Windsurf（桌面 IDE）和 Augment（IDE 插件）形成差异。在便捷性上对标 ChatGPT，但在开发能力上远超 ChatGPT 的沙箱限制。

3. **透明可控的 Agent**：与 Devin 的黑盒模型不同，Teamo 基于 Claude Code——用户知道底层是什么模型，可以通过 CLAUDE.md 精确控制 Agent 行为，可以看到每一步操作。

### 市场空白（Teamo 要填补的位置）

```
                    交互方式
            桌面IDE ←————————→ 纯Web

 简单辅助    Cursor           ChatGPT
   ↑        Windsurf
   |        Augment
   |        Copilot           Replit
   ↓
 自主Agent                    Devin
                              ★ Teamo v1
```

Teamo v1 的目标位置：**纯 Web + 高自主性 + Claude Code 原生能力**。在这个象限中，Devin 是最直接的竞品，但 Teamo 的差异在于：
- 基于 Claude Code（而非自研黑盒模型）
- 用户对实例有完全控制权（而非只能下发任务）
- 定价可以更灵活透明（而非 ACU 黑盒计费）

### 需要警惕的竞争风险

1. **Cursor Cloud Agent 的进化**：Cursor 已推出 Cloud Agent，如果进一步发展为完整的 Web 体验，将直接与 Teamo 竞争
2. **Anthropic 官方可能推出 Claude Code Web 版**：Anthropic 自身最有可能做这个产品，Teamo 需要在 Anthropic 之前建立用户壁垒
3. **Devin 的价格下降**：如果 Devin 推出更便宜的个人版，将在 Web Agent 赛道与 Teamo 直接竞争

### 建议定价区间

基于竞品分析，Teamo v1 建议定价：
- **个人版**：$25-35/月（高于 Cursor Pro $20 但提供完整云端体验，远低于 Devin Core $500/月起步）
- **团队版**：$50-80/人/月（对标 Cursor Teams $40 + Augment Standard $60 的区间）
- **按量计费选项**：考虑 Claude API 成本，可提供基础月费 + 超额按量的混合模式
