# PRD: Teamo v1 MVP — Cloud Claude Code Integration

## Introduction

Teamo v1 replaces the old Teamo agent engine with cloud-based Claude Code instances. Users interact via Web UI, prompts route to per-user Claude CLI processes on a US server, responses stream back via SSE and render in the existing Teamo frontend.

## Goals

- Users can send tasks to a personal Claude Code instance via the Teamo web interface
- Real-time streaming response display (thinking, text, tool use)
- Seamless mode switching between Claude Code and Research (legacy engine)
- Daily credit-based billing for running instances
- Conversation history persisted for returning users
- Production-stable deployment on US Silicon Valley server

## User Stories

### US-001: Instance Manager core API ✅
**Description:** As a developer, I need the instance-manager service to manage per-user Claude CLI processes with full CRUD API.

**Acceptance Criteria:**
- [x] POST /api/instance/create creates per-user Claude CLI process
- [x] POST /api/instance/prompt sends prompt and streams SSE response
- [x] GET /api/instance/status/{user_id} returns instance status
- [x] POST /api/instance/destroy/{user_id} terminates instance
- [x] GET /health returns service health
- [x] All 9 instance-manager tests pass

### US-002: Claude Code Proxy - mode routing and SSE conversion ✅
**Description:** As a developer, I need the proxy to route claude_code mode to instance-manager and convert SSE events to frontend format.

**Acceptance Criteria:**
- [x] mode=claude_code routes to instance-manager
- [x] mode=a2a (Research) routes to legacy backend
- [x] SSE events mapped: text→answer_chunk, thinking→think_chunk, tool_use→tool_call, tool_result→tool_result, done→task_done
- [x] start_answer event sent before streaming with step_conv_id
- [x] Auth extracted from Authorization header or Cookie

### US-003: Frontend ModeSelector component ✅
**Description:** As a user, I want to switch between Claude Code and Research modes via a visual selector.

**Acceptance Criteria:**
- [x] ModeSelector.vue with Claude Code and Research cards
- [x] Default mode is claude_code
- [x] Mode persists in localStorage
- [x] Integrated in chat/index.vue and home/index.vue

### US-004: Credits billing logic layer ✅
**Description:** As a developer, I need billing calculation functions for daily credit deduction.

**Acceptance Criteria:**
- [x] deduct_credits() with priority: free→vip→extend
- [x] check_and_bill() checks balance before deduction
- [x] get_credits_info() returns balance + warning
- [x] All 11 tests pass

### US-005: Deploy to US server ✅
**Description:** As a developer, I need the instance-manager deployed to the US server.

**Acceptance Criteria:**
- [x] instance-manager running on 49.51.47.101:8902 via systemd
- [x] Claude CLI accessible, ANTHROPIC_API_KEY configured
- [x] Service auto-restarts on failure

### US-006: E2E basic flow ✅
**Description:** As a user, I want to type "hi" and see Claude's response in the frontend.

**Acceptance Criteria:**
- [x] Type "hi" → send → Claude responds → frontend renders response
- [x] Screenshot evidence saved

### US-007: Fix proxy test failures
**Description:** As a developer, I need all proxy tests to pass so CI stays green.

**Acceptance Criteria:**
- [ ] Fix 3 test assertion mismatches (response nesting format)
- [ ] All 13 claude-code-proxy tests pass
- [ ] pytest exits with 0 failures

### US-008: MongoDB conversation history persistence
**Description:** As a user, I want my Claude Code conversations saved so I can see them when I return.

**Acceptance Criteria:**
- [ ] Proxy saves user prompt to MongoDB after askAgents call
- [ ] Proxy accumulates and saves Claude response after stream completes
- [ ] Record includes: conv_id, session_group_id, username, query, response, mode, request_time
- [ ] Test verifies conversation saved after streaming

### US-009: Daily billing scheduler
**Description:** As a system, I need to automatically deduct credits daily for running instances.

**Acceptance Criteria:**
- [ ] APScheduler (or equivalent) runs daily at UTC 00:00
- [ ] Queries MongoDB for users with running instances
- [ ] Calls deduct_credits() for each user
- [ ] If balance < 28, calls instance-manager destroy API
- [ ] Scheduler starts with the proxy service

### US-010: Frontend instance status and credits polling
**Description:** As a user, I want to see my instance status and credits balance in the UI.

**Acceptance Criteria:**
- [ ] chat/index.vue calls apiGetInstanceStatus() on mount
- [ ] Polls every 30 seconds
- [ ] Updates ModeSelector instanceStatus and creditsInfo props
- [ ] Status dot shows correct color
- [ ] Verify in browser

### US-011: Stop task functionality ✅
**Description:** As a user, I want to stop a running Claude Code task.

**Acceptance Criteria:**
- [x] askAgentsUserStop API forwards to instance-manager destroy
- [x] SSE connection closes
- [x] Frontend stop button wired

### US-012: Deploy updates to production
**Description:** As a developer, I need updated proxy + billing deployed to production.

**Acceptance Criteria:**
- [ ] Updated claude-code-proxy deployed to 49.51.47.101
- [ ] MongoDB connection configured
- [ ] Billing scheduler running
- [ ] Smoke test passes
- [ ] Stable for 1 hour

## Functional Requirements

- FR-1: Instance-manager manages per-user Claude CLI processes via asyncio subprocess
- FR-2: Proxy converts Claude CLI stream-json to frontend SSE format (start_answer → answer_chunk → task_done)
- FR-3: Mode routing: claude_code → instance-manager, a2a → legacy backend
- FR-4: ModeSelector persists choice to localStorage, defaults to claude_code
- FR-5: Credits billing: 28/day, priority deduction (free→vip→extend), auto-stop on zero
- FR-6: Conversation history saved to MongoDB with session_group_id linkage
- FR-7: Instance status polling updates UI status indicator

## Non-Goals (Out of Scope for MVP)

- Multi-Agent collaboration (multiple Claude instances cooperating)
- File upload to Claude instances
- Project management features
- Team collaboration / shared instances
- Custom CLAUDE.md per user
- Instance spec selection (GPU, memory)
- WebSocket real-time updates (SSE is sufficient)

## Technical Considerations

- US server (49.51.47.101) runs instance-manager; proxy can run co-located or separately
- Claude CLI auth: ANTHROPIC_API_KEY in env (OAuth token expired, using API key instead)
- Frontend is Nuxt 3 in separate teamo-runner repo
- MongoDB already used by existing wowchat-backend
- TAT remote execution for server deployment (no SSH)

## Success Metrics

- User can complete full Claude Code conversation in < 10 seconds first response
- Daily billing deducts correctly for all running instances
- Conversation history viewable on return visit
- Zero unhandled crashes over 24 hours
- Mode switching works without page reload

## Open Questions

- Should proxy and instance-manager be co-located on the same server?
- What's the maximum concurrent Claude instances the US server can handle?
- Should conversation history include tool_use/tool_result details or just final text?
