"""Pydantic models for Claude Code Proxy API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AskAgentsRequest(BaseModel):
    query: str
    mode: str = "claude_code"
    session_group_id: Optional[str] = None
    conv_id: Optional[str] = None


class AskAgentsResponse(BaseModel):
    code: int = 0
    mcp_task_id: str = ""
    result: Optional[Dict[str, Any]] = None


class AskAgentsCheckRequest(BaseModel):
    mcp_task_id: str
    mode: str = "claude_code"


class UserStopRequest(BaseModel):
    mcp_task_id: str
    mode: str = "claude_code"


class InstanceStatusResponse(BaseModel):
    code: int = 0
    result: Dict[str, Any] = Field(default_factory=dict)


# SSE conversion helpers

class FrontendSSEEvent:
    """Format that the existing frontend understands."""

    @staticmethod
    def step(name: str, result: dict, depth: int = 0) -> str:
        import json
        payload = {
            "event": "step",
            "name": name,
            "result": result,
            "status": 1,
            "depth": depth,
        }
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    @staticmethod
    def task_done() -> str:
        import json
        payload = {"event": "task_done"}
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
