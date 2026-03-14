# Teamo v1 — 开发 TODO

> 由 Agent 自动维护，记录全流程进度。每个已完成项链接到 docs/ 下的验收文档。

## Phase 1: 需求收集与澄清
- [x] 需求复述与澄清 → [docs/01-intake/requirements.md](docs/01-intake/requirements.md)
- [x] 用户确认需求 ✅ 2026-03-14

## Phase 2: 市场/竞品/用户洞察
- [x] 竞品 Top 5 识别与功能矩阵 → [docs/02-research/competitive-analysis.md](docs/02-research/competitive-analysis.md)
- [x] 用户声音洞察 → [docs/02-research/user-voice.md](docs/02-research/user-voice.md)
- [x] 社媒趋势分析 → [docs/02-research/social-trends.md](docs/02-research/social-trends.md)
- [x] 关联产品实测（Devin + Claude Code）→ [docs/02-research/product-testing.md](docs/02-research/product-testing.md)
- [x] 调研总结 → [docs/02-research/research-summary.md](docs/02-research/research-summary.md)
- [x] 用户审批调研结果 ✅ 2026-03-15

## Phase 3: 核心价值定位
- [x] 价值主张提炼 → [docs/03-value/core-value.md](docs/03-value/core-value.md)
- [x] 核心用户路径定义 → [docs/03-value/user-journey.md](docs/03-value/user-journey.md)
- [x] 用户确认 ✅ 2026-03-15

## Phase 4: PRD 编写
- [x] 业务模块拆分（4 模块）
- [x] 实例管理服务 PRD → [docs/04-prd/instance-manager.md](docs/04-prd/instance-manager.md)
- [x] Claude Code 代理 API PRD → [docs/04-prd/claude-code-proxy.md](docs/04-prd/claude-code-proxy.md)
- [x] 前端模式切换 PRD → [docs/04-prd/frontend-mode-switch.md](docs/04-prd/frontend-mode-switch.md)
- [x] Credits 计费系统 PRD → [docs/04-prd/credits-billing.md](docs/04-prd/credits-billing.md)
- [x] MVP 范围定义 → [docs/04-prd/mvp-scope.md](docs/04-prd/mvp-scope.md)
- [x] 用户审批 PRD ✅ 2026-03-15

## Phase 5: 测试方案 & 用例设计
- [x] 各模块测试用例表格 → [instance-manager-tests.md](docs/05-test-plan/instance-manager-tests.md) | [claude-code-proxy-tests.md](docs/05-test-plan/claude-code-proxy-tests.md) | [credits-billing-tests.md](docs/05-test-plan/credits-billing-tests.md)
- [x] E2E 测试用例 → [docs/05-test-plan/e2e-tests.md](docs/05-test-plan/e2e-tests.md)
- [x] 冒烟测试清单 → [docs/05-test-plan/smoke-tests.md](docs/05-test-plan/smoke-tests.md)
- [x] 用户确认测试计划 ✅ 2026-03-15

## Phase 6: 开发循环
- [x] 基础模块开发（实例管理服务）→ [instance-manager/](instance-manager/) (9 tests passed)
- [x] 核心模块开发（代理 API + 前端适配）→ [claude-code-proxy/](claude-code-proxy/) (13 tests passed) + [frontend-patch/](frontend-patch/)
- [x] 辅助模块开发（Credits 计费）→ [credits-billing/](credits-billing/) (11 tests passed)
- [x] 全量测试通过 — 33/33 tests passed ✅ 2026-03-15
- [x] 验收报告 ✅ 2026-03-15

## Phase 7: 部署
- [x] 代码推送到 GitHub → https://github.com/teamo-lab/teamo-v1
- [x] 服务器部署（美国硅谷 lhins-28jskt2z / 49.51.47.101）→ instance-manager:8902 + proxy:8901
- [ ] 域名配置 + HTTPS（teamoteam.com，待生产发布时配置）
- [x] 冒烟测试通过 — 6/6 PASS ✅ 2026-03-15
- [x] 前端集成 ModeSelector 到 teamo-frontend ✅ 2026-03-15

## Phase 8: 本地 E2E 验证
- [x] 前端构建成功（nuxt build）✅ 2026-03-15
- [x] Playwright 本地测试 — 6/6 PASS ✅ 2026-03-15
- [x] 后端服务冒烟测试 — 6/6 PASS ✅ 2026-03-15
- [ ] 用户审批发布到生产

## Phase 9: Dashboard & 可观测体系
- [x] 关键指标定义 → [docs/09-dashboard/metrics.md](docs/09-dashboard/metrics.md)
- [ ] Dashboard 搭建（待生产发布后接入 Grafana）
- [ ] 部署验证

## Phase 10: 交付
- [x] 交付清单 → [docs/10-delivery/delivery-checklist.md](docs/10-delivery/delivery-checklist.md)
- [ ] 用户审批发布到生产
- [ ] 用户签收
