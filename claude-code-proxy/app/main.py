"""Claude Code Proxy — FastAPI routes that bridge frontend and instance-manager.

For claude_code mode: routes to instance-manager.
For other modes: forwards transparently to legacy wowchat-backend.
Can run standalone for development/testing.
"""

import hashlib
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.proxy import (
    _forward_to_legacy,
    _forward_stream_legacy,
    get_instance_status,
    handle_ask_agents,
    handle_user_stop,
    stream_check,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Claude Code Proxy", version="1.0.0")


def _get_user_id(headers: dict) -> str:
    """Extract user_id from Authorization header or Cookie.

    The frontend stores the JWT in a cookie named 'Authorization'.
    """
    auth = headers.get("authorization", "")
    if not auth:
        # Parse from Cookie header
        cookie = headers.get("cookie", "")
        for part in cookie.split(";"):
            part = part.strip()
            if part.startswith("Authorization="):
                auth = part[len("Authorization="):]
                auth = auth.strip('"')
                break
    if not auth:
        raise HTTPException(status_code=401, detail={"code": 30, "message": "session_expire"})
    token = auth.replace("Bearer ", "").strip()
    # Use a hash for a filesystem-safe, stable user_id
    return hashlib.md5(token.encode()).hexdigest()[:16]


def _get_headers(request: Request) -> dict:
    """Extract forwarding-relevant headers from the incoming request."""
    return dict(request.headers)


@app.post("/api/engine/askAgents")
async def ask_agents(request: Request):
    body = await request.json()
    headers = _get_headers(request)
    mode = body.get("mode", "a2a")

    if mode == "claude_code":
        user_id = _get_user_id(headers)
        return await handle_ask_agents(
            user_id=user_id,
            query=body.get("query", ""),
            mode=mode,
            session_group_id=body.get("session_group_id"),
            headers=headers,
        )
    else:
        # Forward full original body to legacy backend
        return await _forward_to_legacy(
            "/api/engine/askAgents", body, headers
        )


@app.post("/api/engine/askAgentsCheck")
async def ask_agents_check(request: Request):
    body = await request.json()
    headers = _get_headers(request)
    mode = body.get("mode", "a2a")
    task_id = body.get("mcp_task_id", "")

    if mode != "claude_code":
        # Forward full body to legacy backend as SSE stream
        async def legacy_stream():
            async for line in _forward_stream_legacy(
                "/api/engine/askAgentsCheck", body, headers
            ):
                yield line
        return StreamingResponse(legacy_stream(), media_type="text/event-stream")

    async def event_stream():
        async for line in stream_check(task_id, mode, headers=headers, body=body):
            yield line

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/engine/askAgentsUserStop")
async def ask_agents_user_stop(request: Request):
    body = await request.json()
    headers = _get_headers(request)
    mode = body.get("mode", "a2a")

    if mode != "claude_code":
        return await _forward_to_legacy(
            "/api/engine/askAgentsUserStop", body, headers
        )

    user_id = _get_user_id(headers)
    return await handle_user_stop(
        body.get("mcp_task_id", ""), user_id, mode, headers=headers
    )


@app.get("/api/engine/instanceStatus")
async def instance_status(request: Request):
    headers = _get_headers(request)
    user_id = _get_user_id(headers)
    status = await get_instance_status(user_id)
    return {"code": 0, "result": status}
