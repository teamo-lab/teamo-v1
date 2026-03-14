"""Claude Code Proxy — FastAPI routes that bridge frontend and instance-manager.

Designed to integrate into wowchat-backend as a new router module.
Can also run standalone for development/testing.
"""

import logging
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.models import (
    AskAgentsCheckRequest,
    AskAgentsRequest,
    AskAgentsResponse,
    UserStopRequest,
)
from app.proxy import (
    get_instance_status,
    handle_ask_agents,
    handle_user_stop,
    stream_check,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Claude Code Proxy", version="1.0.0")


def _get_user_id(authorization: Optional[str] = None) -> str:
    """Extract user_id from auth header. In production, this validates JWT."""
    if not authorization:
        raise HTTPException(status_code=401, detail={"code": 30, "message": "session_expire"})
    # Simplified: in production, decode JWT from Cookie
    return authorization.replace("Bearer ", "")


@app.post("/api/engine/askAgents")
async def ask_agents(
    req: AskAgentsRequest,
    authorization: Optional[str] = Header(None),
):
    user_id = _get_user_id(authorization)
    result = await handle_ask_agents(
        user_id=user_id,
        query=req.query,
        mode=req.mode,
        session_group_id=req.session_group_id,
    )
    return result


@app.post("/api/engine/askAgentsCheck")
async def ask_agents_check(req: AskAgentsCheckRequest):
    async def event_stream():
        async for line in stream_check(req.mcp_task_id, req.mode):
            yield line

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/engine/askAgentsUserStop")
async def ask_agents_user_stop(
    req: UserStopRequest,
    authorization: Optional[str] = Header(None),
):
    user_id = _get_user_id(authorization)
    return await handle_user_stop(req.mcp_task_id, user_id, req.mode)


@app.get("/api/engine/instanceStatus")
async def instance_status(
    authorization: Optional[str] = Header(None),
):
    user_id = _get_user_id(authorization)
    status = await get_instance_status(user_id)
    return {"code": 0, "result": status}
