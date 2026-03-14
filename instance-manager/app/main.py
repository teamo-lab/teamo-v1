"""Instance Manager — FastAPI service for managing per-user Claude Code instances."""

import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.config import CONFIG
from app.instance import InstanceManager
from app.models import (
    CreateRequest,
    HealthResponse,
    PromptRequest,
    StatusResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Teamo Instance Manager", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(active_instances=InstanceManager.active_count())


@app.post("/api/instance/create")
async def create_instance(req: CreateRequest):
    inst = await InstanceManager.create(req.user_id)
    return {
        "status": inst.info.status.value,
        "user_id": inst.info.user_id,
        "session_id": inst.info.session_id,
    }


@app.get("/api/instance/status/{user_id}", response_model=StatusResponse)
async def get_status(user_id: str):
    inst = InstanceManager.get(user_id)
    if inst is None or inst.info.status == "stopped":
        return StatusResponse(status="stopped")

    uptime = None
    if inst.info.created_at:
        uptime = int((datetime.utcnow() - inst.info.created_at).total_seconds())

    return StatusResponse(
        status=inst.info.status.value,
        created_at=inst.info.created_at.isoformat() if inst.info.created_at else None,
        uptime_seconds=uptime,
        session_id=inst.info.session_id,
    )


@app.post("/api/instance/prompt")
async def send_prompt(req: PromptRequest):
    inst = InstanceManager.get(req.user_id)
    if inst is None:
        inst = await InstanceManager.create(req.user_id)

    async def event_stream():
        async for line in inst.send_prompt(req.prompt, req.cwd):
            yield line

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/instance/destroy/{user_id}")
async def destroy_instance(user_id: str):
    ok = await InstanceManager.destroy(user_id)
    return {"status": "stopped" if ok else "not_found", "user_id": user_id}
