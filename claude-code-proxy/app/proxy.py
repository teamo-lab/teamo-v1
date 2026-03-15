"""Claude Code Proxy — routes requests between frontend and instance-manager.

For claude_code mode: handles locally via instance-manager.
For other modes (a2a, research, etc.): forwards to legacy wowchat-backend.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import AsyncIterator, Optional

import httpx

from app.config import CONFIG
from app.history import save_conversation
from app.models import FrontendSSEEvent
from app.sse_converter import convert_instance_sse

logger = logging.getLogger(__name__)

# In-memory task store: task_id -> {user_id, mode, session_group_id, ...}
_tasks: dict = {}


async def _forward_to_legacy(
    path: str, body: dict, headers: dict, method: str = "POST"
) -> dict:
    """Forward a JSON request to legacy backend and return JSON response."""
    fwd_headers = {k: v for k, v in headers.items()
                   if k.lower() in ("authorization", "cookie", "content-type")}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.request(
            method,
            f"{CONFIG.legacy_backend_url}{path}",
            json=body,
            headers=fwd_headers,
        )
        try:
            return resp.json()
        except Exception:
            return {"code": -1, "message": f"Legacy backend error: {resp.status_code}"}


async def _forward_stream_legacy(
    path: str, body: dict, headers: dict
) -> AsyncIterator[str]:
    """Forward request to legacy backend and stream SSE response."""
    fwd_headers = {k: v for k, v in headers.items()
                   if k.lower() in ("authorization", "cookie", "content-type")}
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{CONFIG.legacy_backend_url}{path}",
                json=body,
                headers=fwd_headers,
            ) as resp:
                async for line in resp.aiter_lines():
                    yield line + "\n"
    except httpx.HTTPError as exc:
        logger.exception("Legacy stream error: %s", exc)
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"


async def handle_ask_agents(
    user_id: str,
    query: str,
    mode: str,
    session_group_id: Optional[str] = None,
    headers: Optional[dict] = None,
) -> dict:
    """Route askAgents based on mode.

    claude_code → instance-manager; other modes → legacy backend.
    """
    if mode == "claude_code":
        return await _ask_claude_code(user_id, query, session_group_id)
    else:
        # Forward to legacy wowchat-backend
        body = {"query": query, "mode": mode}
        if session_group_id:
            body["session_group_id"] = session_group_id
        return await _forward_to_legacy(
            "/api/engine/askAgents", body, headers or {}
        )


async def _ask_claude_code(
    user_id: str, query: str, session_group_id: Optional[str]
) -> dict:
    """Create a task entry and return task_id.

    Does NOT call instance-manager here — stream_check does the actual streaming.
    """
    task_id = uuid.uuid4().hex[:16]

    _tasks[task_id] = {
        "user_id": user_id,
        "mode": "claude_code",
        "query": query,
        "session_group_id": session_group_id or uuid.uuid4().hex[:12],
        "created_at": datetime.utcnow().isoformat(),
    }

    return {"code": 0, "result": {"mcp_task_id": task_id}}


async def stream_check(
    task_id: str,
    mode: str,
    headers: Optional[dict] = None,
    body: Optional[dict] = None,
) -> AsyncIterator[str]:
    """Stream SSE events for askAgentsCheck."""
    if mode != "claude_code":
        # Forward to legacy backend
        async for line in _forward_stream_legacy(
            "/api/engine/askAgentsCheck",
            body or {"mcp_task_id": task_id, "mode": mode},
            headers or {},
        ):
            yield line
        return

    task = _tasks.get(task_id)
    if not task:
        yield FrontendSSEEvent.step("error", {"message": "Task not found"})
        yield FrontendSSEEvent.task_done()
        return

    user_id = task["user_id"]
    query = task["query"]
    session_group_id = task.get("session_group_id", "")
    step_conv_id = uuid.uuid4().hex[:12]

    # Frontend requires start_answer before answer_chunk events
    yield FrontendSSEEvent.step(
        "start_answer", {"step_conv_id": step_conv_id, "message": ""}
    )

    response_chunks: list[str] = []

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
                    for converted in convert_instance_sse(
                        raw_line, step_conv_id=step_conv_id
                    ):
                        yield converted
                    # Accumulate text content for history
                    if raw_line.startswith("data: "):
                        try:
                            evt = json.loads(raw_line[6:])
                            if evt.get("type") == "text":
                                response_chunks.append(evt.get("content", ""))
                        except (json.JSONDecodeError, KeyError):
                            pass
    except httpx.HTTPError as exc:
        logger.exception("Stream error for task %s", task_id)
        yield FrontendSSEEvent.step("error", {"message": str(exc)})
        yield FrontendSSEEvent.task_done()

    # Save conversation history to MongoDB
    full_response = "".join(response_chunks)
    if full_response:
        try:
            await save_conversation(
                conv_id=task_id,
                session_group_id=session_group_id,
                username=user_id,
                query=query,
                response=full_response,
            )
        except Exception:
            logger.exception("Failed to save history for task %s", task_id)


async def handle_user_stop(
    task_id: str,
    user_id: str,
    mode: str,
    headers: Optional[dict] = None,
) -> dict:
    """Stop a running task."""
    if mode != "claude_code":
        return await _forward_to_legacy(
            "/api/engine/askAgentsUserStop",
            {"mcp_task_id": task_id, "mode": mode},
            headers or {},
        )

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
            if resp.status_code == 200:
                return resp.json()
            return {"status": "stopped"}
    except Exception:
        return {"status": "unknown"}
