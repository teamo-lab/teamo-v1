# Ralph Agent Instructions — Teamo v1

You are an autonomous coding agent working on the Teamo v1 project.

## Project Context

Teamo v1 replaces the old Teamo agent engine with cloud-based Claude Code instances. Architecture:
- **instance-manager** (FastAPI, port 8902): Manages per-user Claude CLI processes
- **claude-code-proxy** (FastAPI, port 8901): Bridges frontend ↔ instance-manager, SSE format conversion
- **Frontend** (Nuxt 3): teamo-runner at /Users/zhangyiming/teamo-runner/
- **US Server**: 49.51.47.101 (lhins-28jskt2z, na-siliconvalley)

## Your Task

1. Read the PRD at `scripts/ralph/prd.json`
2. Read the progress log at `scripts/ralph/progress.txt` (check Codebase Patterns section first)
3. Check you're on the correct branch from PRD `branchName`. If not, check it out or create from main.
4. Pick the **highest priority** user story where `passes: false`
5. Implement that single user story
6. Run quality checks (pytest for Python modules)
7. Update CLAUDE.md files if you discover reusable patterns
8. If checks pass, commit ALL changes with message: `feat: [Story ID] - [Story Title]`
9. Update the PRD to set `passes: true` for the completed story
10. Append your progress to `scripts/ralph/progress.txt`

## Codebase Patterns

- Python services use FastAPI + uvicorn
- Tests use pytest with async support
- Instance-manager spawns Claude CLI via asyncio.create_subprocess_exec
- Frontend SSE requires: start_answer → answer_chunk(s) → task_done events
- Each SSE event needs step_conv_id for frontend matching
- Deploy to US server uses TAT (Tencent Cloud remote execution)
- Frontend patches go in frontend-patch/ directory (copied to teamo-runner/)

## Progress Report Format

APPEND to scripts/ralph/progress.txt (never replace, always append):
```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
---
```

## Quality Requirements

- ALL commits must pass pytest
- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns

## Stop Condition

After completing a user story, check if ALL stories have `passes: true`.
If ALL stories are complete, reply with:
<promise>COMPLETE</promise>

If there are still stories with `passes: false`, end your response normally.

## Important

- Work on ONE story per iteration
- Commit frequently
- Keep tests green
- Read Codebase Patterns before starting
