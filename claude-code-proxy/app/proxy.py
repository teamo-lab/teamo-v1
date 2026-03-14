"""Claude Code Proxy — routes requests between frontend and instance-manager."""

import json
import logging
import uuid
from datetime import datetime
from typing import AsyncIterator, Callable, Optional

import httpx

from app.config import CONFIG
from app.models import FrontendSSEEvent
from app.sse_converter import convert_instance_sse

logger = logging.getLogger(__name__)

# In-memory task store: task_id -> {user_id, mode, session_group_id, ...}
_tasks: dict = {}


async def handle_ask_agents(
    user_id: str,
    query: str,
    mode: str,
    session_group_id: Optional[str] = None,
    mcp_handler: Optional[Callable] = None,
) -> dict:
    """Route askAgents based on mode.

    Returns dict with mcp_task_id (for claude_code) or delegates to mcp_handler.
    """
    if mode == "claude_code":
        return await _ask_claude_code(user_id, query, session_group_id)
    else:
        # Delegate to old MCP engine (Research mode)
        if mcp_handler:
            return await mcp_handler(user_id, query, session_group_id)
        return {"code": 0, "mcp_task_id": "", "result": {"error": "no_mcp_handler"}}


async def _ask_claude_code(
    user_id: str, query: str, session_group_id: Optional[str]
) -> dict:
    """Forward prompt to instance-manager and return task_id."""
    task_id = uuid.uuid4().hex[:16]

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{CONFIG.instance_manager_url}/api/instance/prompt",
            json={"user_id": user_id, "prompt": query},
        )
        # We don't consume the stream here — askAgentsCheck will do that

    _tasks[task_id] = {
        "user_id": user_id,
        "mode": "claude_code",
        "query": query,
        "session_group_id": session_group_id or uuid.uuid4().hex[:12],
        "created_at": datetime.utcnow().isoformat(),
    }

    return {"code": 0, "mcp_task_id": task_id}


async def stream_check(
    task_id: str,
    mode: str,
    mcp_stream_handler: Optional[Callable] = None,
) -> AsyncIterator[str]:
    """Stream SSE events for askAgentsCheck."""
    if mode != "claude_code":
        if mcp_stream_handler:
            async for line in mcp_stream_handler(task_id):
                yield line
        return

    task = _tasks.get(task_id)
    if not task:
        yield FrontendSSEEvent.step("error", {"message": "Task not found"})
        yield FrontendSSEEvent.task_done()
        return

    user_id = task["user_id"]
    query = task["query"]

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{CONFIG.instance_manager_url}/api/instance/prompt",
                json={"user_id": user_id, "prompt": query},
            ) as resp:
                async for raw_line in resp.aiter_lines():
                    if not raw_line:
                        continue
                    for converted in convert_instance_sse(raw_line):
                        yield converted
    except httpx.HTTPError as exc:
        logger.exception("Stream error for task %s", task_id)
        yield FrontendSSEEvent.step("error", {"message": str(exc)})
        yield FrontendSSEEvent.task_done()


async def handle_user_stop(
    task_id: str,
    user_id: str,
    mode: str,
    mcp_stop_handler: Optional[Callable] = None,
) -> dict:
    """Stop a running task."""
    if mode != "claude_code":
        if mcp_stop_handler:
            return await mcp_stop_handler(task_id, user_id)
        return {"code": 0}

    task = _tasks.get(task_id)
    if not task:
        return {"code": -1, "message": "Task not found"}

    # Tell instance-manager to stop
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{CONFIG.instance_manager_url}/api/instance/destroy/{user_id}"
            )
    except httpx.HTTPError:
        pass

    _tasks.pop(task_id, None)
    return {"code": 0, "message": "stopped"}


async def get_instance_status(user_id: str) -> dict:
    """Get instance status from instance-manager."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{CONFIG.instance_manager_url}/api/instance/status/{user_id}"
            )
            return resp.json()
    except httpx.HTTPError:
        return {"status": "unknown"}
