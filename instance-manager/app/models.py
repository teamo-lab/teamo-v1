"""Pydantic models for Instance Manager API."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class InstanceStatus(str, Enum):
    running = "running"
    creating = "creating"
    stopped = "stopped"
    error = "error"


class ClaudeInstance:
    """In-memory representation of a user's Claude Code instance."""

    def __init__(self, user_id: str, home_dir: str):
        self.user_id = user_id
        self.status: InstanceStatus = InstanceStatus.creating
        self.process_pid: int = 0
        self.home_dir: str = home_dir
        self.created_at: datetime = datetime.utcnow()
        self.last_active_at: datetime = datetime.utcnow()
        self.session_id: str = ""
        self.restart_count: int = 0


# --- Request Models ---

class PromptRequest(BaseModel):
    user_id: str
    prompt: str
    session_id: Optional[str] = None
    cwd: Optional[str] = None


class CreateRequest(BaseModel):
    user_id: str


class DestroyRequest(BaseModel):
    user_id: str


# --- Response Models ---

class StatusResponse(BaseModel):
    status: str
    created_at: Optional[str] = None
    uptime_seconds: Optional[int] = None
    session_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "instance-manager"
    active_instances: int = 0


# --- SSE Event Types ---

class SSEEventType(str, Enum):
    text = "text"
    thinking = "thinking"
    tool_use = "tool_use"
    tool_result = "tool_result"
    done = "done"
    error = "error"
