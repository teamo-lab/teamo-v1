# Teamo v1 — 需求摘要

> Phase 1 | 创建时间: 2026-03-14 18:45 | 状态: 待确认

## 用户原始描述

将 Teamo 前端不再打向后端默认的 Teamo Agent，而是用云端 Claude Code 作为默认 Agent 引擎，彻底废弃老引擎。在首页发起任务本质上是向用户专属的 Claude Code 云端实例发起任务。

## Agent 理解

### 产品定义（一句话）

Teamo v1 = 现有 Teamo 平台 + 云端 Claude Code 作为默认 Agent 引擎，每个用户拥有专属的持久化 Claude Code 云端实例。

### 核心变更

| 维度 | 旧版（Research 模式） | 新版（Claude Code 模式） |
|------|----------------------|------------------------|
| Agent 引擎 | wowchat-backend 自研 Agent | 云端 Claude Code 实例 |
| 实例模型 | 共享服务 | 用户专属实例（1:1） |
| 计费 | 按 API 调用计费 | 按实例运行时长计费（28 credits/天） |
| 能力 | 对话 + 搜索 | 完整 Claude Code 能力（代码、工具、文件） |

## 澄清 Q&A

### Q1: 用户专属实例 vs 共享实例？
**A: 用户专属**。每个用户一个独立的 Claude Code 云端实例。

### Q2: MVP 范围？
**A: P0 + P1**
- P0: 发起任务 → Claude Code 执行 → 流式返回
- P1: 用户注册/登录、历史记录、额度（credits）管理

### Q3: 前端策略？
**A: 增量开发**。在现有 teamo-frontend 基础上：
- 输入框下方新增**模式卡片**
- 默认 = "Claude Code 模式"（新引擎）
- 可切换 = "Research 模式"（旧引擎）

### Q4: 后端策略？
**A: wowchat-backend 增加 Claude Code 代理模块**。
- 新模块负责将请求代理到用户对应的云端 Claude Code 实例
- deploy-claude-cloud 二次开发，支持多用户实例管理

### Q5: 实例生命周期？
**A: 持久运行**。
- 用户首次使用时创建实例，长期运行
- 仅当用户 credits = 0 时关机
- 计费规则：1 credit = 0.035 元，一台机器约 1 元/天 ≈ 28 credits/天
- 用户无法手动关停机器

### Q6: 部署目标？
**A: 美国服务器**。与 Claude Code 云端实例同机房，减少跨区域流量费。
- 当前美国服务器：`lhins-28jskt2z`（na-siliconvalley, 49.51.47.101）

### Q7: 老引擎兼容？
**A: 兼容**。老引擎保留为 "Research 模式"，用户可在前端切换。

## MVP 功能清单

### P0 — 核心链路
| # | 功能 | 描述 |
|---|------|------|
| 1 | Claude Code 实例管理服务 | 基于 deploy-claude-cloud 二开，支持创建/销毁/查询用户专属实例 |
| 2 | Claude Code 代理 API | wowchat-backend 新模块，转发请求到用户实例，流式返回 |
| 3 | 前端模式切换 | 输入框下方模式卡片，默认 Claude Code 模式，可切换 Research 模式 |
| 4 | 流式对话 | 用户发送消息 → 后端代理 → Claude Code 执行 → SSE 流式返回前端 |

### P1 — 基础体系
| # | 功能 | 描述 |
|---|------|------|
| 5 | Credits 计费系统 | 按天扣费（28 credits/天），余额为 0 时自动关机 |
| 6 | 用户实例状态展示 | 前端显示实例运行状态（运行中/已关机/创建中） |
| 7 | 对话历史 | 保存 Claude Code 模式下的对话记录 |
| 8 | 复用现有用户系统 | 登录/注册/额度充值复用 wowchat-backend 已有模块 |

## 技术约束
- 前端：Nuxt 3 + Vue 3（现有 teamo-frontend 技术栈）
- 后端：Python FastAPI（现有 wowchat-backend 技术栈）
- Claude Code 实例服务：Python FastAPI（deploy-claude-cloud 技术栈）
- 部署地域：美国硅谷（na-siliconvalley）
- 通信协议：HTTP + SSE（与现有前端一致）
