"""Convert Claude Code SSE events to frontend-compatible SSE format.

Mapping (from PRD):
  Claude Code {"type":"text","content":"..."} → frontend step/answer_chunk
  Claude Code {"type":"thinking","content":"..."} → frontend step/think_chunk
  Claude Code {"type":"tool_use",...} → frontend step/tool_call
  Claude Code {"type":"tool_result",...} → frontend step/tool_result
  Claude Code {"type":"done",...} → frontend task_done
  Claude Code {"type":"error",...} → frontend step/error
"""

import json
from typing import List

from app.models import FrontendSSEEvent


def convert_instance_sse(raw_line: str, step_conv_id: str = "") -> List[str]:
    """Convert a single SSE data line from instance-manager to frontend SSE lines.

    Args:
        raw_line: A line like 'data: {"type":"text","content":"Hello"}\n\n'
        step_conv_id: Conversation step ID for correlating answer chunks.

    Returns:
        List of frontend-compatible SSE strings.
    """
    line = raw_line.strip()
    if not line.startswith("data:"):
        return []

    json_str = line[len("data:"):].strip()
    if not json_str:
        return []

    try:
        event = json.loads(json_str)
    except json.JSONDecodeError:
        return []

    return _map_event(event, step_conv_id)


def _map_event(event: dict, step_conv_id: str = "") -> List[str]:
    etype = event.get("type", "")

    if etype == "text":
        return [FrontendSSEEvent.step(
            "answer_chunk",
            {"step_conv_id": step_conv_id, "message": event.get("content", "")},
        )]

    if etype == "thinking":
        return [FrontendSSEEvent.step(
            "think_chunk",
            {"step_conv_id": step_conv_id, "message": event.get("content", "")},
        )]

    if etype == "tool_use":
        return [FrontendSSEEvent.step(
            "tool_call",
            {
                "step_conv_id": step_conv_id,
                "tool": event.get("tool", ""),
                "input": event.get("input", {}),
            },
        )]

    if etype == "tool_result":
        return [FrontendSSEEvent.step(
            "tool_result",
            {"step_conv_id": step_conv_id, "output": event.get("output", "")},
        )]

    if etype == "done":
        return [FrontendSSEEvent.task_done()]

    if etype == "error":
        return [FrontendSSEEvent.step(
            "error",
            {"message": event.get("message", "Unknown error")},
        )]

    return []
