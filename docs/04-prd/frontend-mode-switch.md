# 前端模式切换 PRD

> Phase 4 | 模块: frontend-mode-switch | 创建时间: 2026-03-15

## 模块概述

在现有 Teamo 前端输入框下方新增模式切换卡片，支持 Claude Code 模式（默认）和 Research 模式（旧引擎）。

## 用户故事

- 作为用户，我希望默认使用 Claude Code 模式，获得最强 AI 编码能力
- 作为用户，我希望可以切换到 Research 模式进行搜索和研究任务
- 作为用户，我希望看到当前实例状态（运行中/创建中/已关机）

## 功能清单

| # | 功能 | 优先级 | MVP | 描述 |
|---|------|--------|-----|------|
| 1 | 模式卡片 UI | P0 | Yes | 输入框下方展示当前模式，可点击切换 |
| 2 | Claude Code 模式标识 | P0 | Yes | 显示 Claude Code 图标 + "Claude Code" 标签 |
| 3 | Research 模式标识 | P0 | Yes | 显示搜索图标 + "Research" 标签 |
| 4 | 实例状态指示 | P1 | Yes | Claude Code 模式下显示实例状态小圆点 |
| 5 | Credits 余额显示 | P1 | Yes | 显示剩余 credits 和预估天数 |

## 页面设计

### 输入框区域改造

```
┌─────────────────────────────────────────┐
│  [输入框：输入你的任务...]              │
│                                         │
├─────────────────────────────────────────┤
│  [🟢 Claude Code] ←→ [🔍 Research]     │
│   默认模式           点击切换            │
│   实例运行中 · 剩余 156 credits         │
└─────────────────────────────────────────┘
```

### 模式卡片组件

```vue
<!-- ModeSelector.vue -->
<div class="mode-selector">
  <div
    class="mode-card"
    :class="{ active: mode === 'claude_code' }"
    @click="switchMode('claude_code')"
  >
    <span class="status-dot" :class="instanceStatus" />
    <span class="icon">⚡</span>
    <span class="label">Claude Code</span>
  </div>
  <div
    class="mode-card"
    :class="{ active: mode === 'research' }"
    @click="switchMode('research')"
  >
    <span class="icon">🔍</span>
    <span class="label">Research</span>
  </div>
</div>
```

## 交互规则

1. **默认模式**: 新用户默认 Claude Code 模式
2. **切换行为**: 点击另一个模式卡片立即切换，不需要确认
3. **记忆选择**: 模式选择保存到 localStorage（`chatMode`），下次打开恢复
4. **状态指示**:
   - 🟢 绿色 = 实例运行中
   - 🟡 黄色 = 实例创建中
   - 🔴 红色 = 实例已关机（credits 不足）
   - 无圆点 = Research 模式
5. **首次创建提示**: 第一次使用 Claude Code 模式时，显示"正在为你启动专属实例..."

## 技术实现

### 关键改动文件

1. **`src/mixin/chatcore.js`** — `getModeValue()` 增加 `claude_code` 映射
2. **`src/components/ModeSelector.vue`** — 新增模式选择器组件
3. **`src/components/Home/ChatInput.vue`** — 集成 ModeSelector
4. **`src/views/chat/index.vue`** — 引入 ModeSelector
5. **`src/api/engine.js`** — 新增 `apiGetInstanceStatus()` 接口

### 数据流

```
ModeSelector.switchMode('claude_code')
  → this.mode = 'claude_code'
  → localStorage.setItem('chatMode', 'claude_code')
  → chatcore.getModeValue() 返回 'claude_code'
  → requestParams.mode = 'claude_code'
  → apiAskAgents() 发送到后端
  → 后端根据 mode 路由到 Claude Code 或 MCP
```
