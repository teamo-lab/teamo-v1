"""Instance lifecycle management for Claude Code instances.

NOTE: Uses asyncio.create_subprocess_exec (NOT shell exec) for safe,
non-shell subprocess invocation - equivalent to Node.js execFile.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Dict, Optional

from app.config import CONFIG
from app.models import ClaudeInstance, InstanceStatus, SSEEventType

logger = logging.getLogger(__name__)


class InstanceManager:
    """Manages per-user Claude Code instances."""

    _instances: Dict[str, "ManagedInstance"] = {}

    @classmethod
    async def create(cls, user_id: str) -> "ManagedInstance":
        if user_id in cls._instances:
            existing = cls._instances[user_id]
            if existing.is_alive():
                logger.info("Reusing existing instance for user %s", user_id)
                return existing

        home_dir = CONFIG.instance_base_dir / user_id
        home_dir.mkdir(parents=True, exist_ok=True)

        inst = ManagedInstance(user_id, str(home_dir))
        await inst.start()
        cls._instances[user_id] = inst
        logger.info(
            "Created instance for user %s, pid=%s", user_id, inst.info.process_pid
        )
        return inst

    @classmethod
    def get(cls, user_id: str) -> Optional["ManagedInstance"]:
        return cls._instances.get(user_id)

    @classmethod
    async def destroy(cls, user_id: str) -> bool:
        inst = cls._instances.get(user_id)
        if inst is None:
            return False
        await inst.stop()
        inst.info.status = InstanceStatus.stopped
        return True

    @classmethod
    def active_count(cls) -> int:
        return sum(1 for i in cls._instances.values() if i.is_alive())


class ManagedInstance:
    """A single user's Claude Code environment."""

    def __init__(self, user_id: str, home_dir: str):
        self.info = ClaudeInstance(user_id=user_id, home_dir=home_dir)
        self._process: Optional[asyncio.subprocess.Process] = None

    def is_alive(self) -> bool:
        if self.info.status == InstanceStatus.stopped:
            return False
        if self._process and self._process.returncode is not None:
            return False
        return self.info.status == InstanceStatus.running

    async def start(self) -> None:
        """Mark instance as running. Actual CLI is spawned per-prompt."""
        self.info.status = InstanceStatus.running
        self.info.process_pid = 1  # Placeholder; real PID set per prompt
        self.info.session_id = uuid.uuid4().hex[:12]
        self.info.created_at = datetime.utcnow()

    async def stop(self) -> None:
        if self._process and self._process.returncode is None:
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=5)
            except (ProcessLookupError, asyncio.TimeoutError):
                pass
        self.info.status = InstanceStatus.stopped

    async def _ensure_alive(self) -> None:
        """If process crashed, restart it."""
        if self._process and self._process.returncode is not None:
            logger.warning(
                "Instance %s crashed (rc=%s), restarting...",
                self.info.user_id,
                self._process.returncode,
            )
            self.info.restart_count += 1
            self._process = None
            self.info.status = InstanceStatus.running

    async def send_prompt(
        self, prompt: str, cwd: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Spawn claude CLI with -p flag and yield SSE lines.

        Uses asyncio safe subprocess (no shell) to invoke the Claude CLI.
        """
        await self._ensure_alive()

        if self.info.status != InstanceStatus.running:
            yield _sse_line(SSEEventType.error, {"message": "Instance not running"})
            return

        cmd = [CONFIG.claude_bin, "-p", prompt, "--output-format", "stream-json"]
        if CONFIG.claude_model:
            cmd.extend(["--model", CONFIG.claude_model])

        env = {
            "HOME": self.info.home_dir,
            "PATH": "/usr/local/bin:/usr/bin:/bin",
        }
        if cwd is None:
            cwd = self.info.home_dir

        proc = None
        try:
            # asyncio safe subprocess (no shell invocation)
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )
            self._process = proc
            self.info.process_pid = proc.pid
            self.info.last_active_at = datetime.utcnow()

            async for sse_line in self._read_stream(proc):
                yield sse_line

        except asyncio.TimeoutError:
            yield _sse_line(SSEEventType.error, {"message": "Prompt timeout"})
            if proc and proc.returncode is None:
                proc.kill()
                await proc.wait()
        except Exception as exc:
            logger.exception("Prompt failed for user %s", self.info.user_id)
            yield _sse_line(SSEEventType.error, {"message": str(exc)})

    async def _read_stream(
        self, proc: asyncio.subprocess.Process
    ) -> AsyncIterator[str]:
        """Read stream-json output from Claude CLI and yield SSE lines."""
        while True:
            try:
                raw = await asyncio.wait_for(
                    proc.stdout.readline(),
                    timeout=CONFIG.claude_timeout_seconds,
                )
            except asyncio.TimeoutError:
                yield _sse_line(SSEEventType.error, {"message": "Read timeout"})
                proc.kill()
                await proc.wait()
                return

            if not raw:
                break

            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            for sse in _convert_claude_event(event):
                yield sse

        await proc.wait()
        yield _sse_line(SSEEventType.done, {"session_id": self.info.session_id})


def _sse_line(event_type: SSEEventType, data: dict) -> str:
    payload = {"type": event_type.value, **data}
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _convert_claude_event(event: dict) -> list:
    """Convert Claude stream-json event to SSE lines."""
    lines = []
    etype = event.get("type", "")

    if etype == "assistant":
        content_blocks = event.get("message", {}).get("content", [])
        for block in content_blocks:
            btype = block.get("type", "")
            if btype == "text":
                lines.append(
                    _sse_line(SSEEventType.text, {"content": block.get("text", "")})
                )
            elif btype == "thinking":
                lines.append(
                    _sse_line(
                        SSEEventType.thinking,
                        {"content": block.get("thinking", "")},
                    )
                )
            elif btype == "tool_use":
                lines.append(
                    _sse_line(
                        SSEEventType.tool_use,
                        {
                            "tool": block.get("name", ""),
                            "input": block.get("input", {}),
                        },
                    )
                )
            elif btype == "tool_result":
                lines.append(
                    _sse_line(
                        SSEEventType.tool_result,
                        {"output": block.get("content", "")},
                    )
                )

    elif etype == "content_block_delta":
        delta = event.get("delta", {})
        dtype = delta.get("type", "")
        if dtype == "text_delta":
            lines.append(
                _sse_line(SSEEventType.text, {"content": delta.get("text", "")})
            )
        elif dtype == "thinking_delta":
            lines.append(
                _sse_line(
                    SSEEventType.thinking, {"content": delta.get("thinking", "")}
                )
            )

    elif etype == "result":
        pass  # Handled by done event after stream ends

    return lines
