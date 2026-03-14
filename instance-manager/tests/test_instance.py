"""Unit and integration tests for Instance Manager.

Test plan: docs/05-test-plan/instance-manager-tests.md
9 test cases covering create, prompt, status, destroy, duplicate,
nonexistent user, timeout, crash recovery, health check.
"""

import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models import InstanceStatus


# ============================================================
# Test 1: Create instance successfully
# ============================================================
class TestCreateInstance:
    def test_create_instance_returns_running(self, app_client, mock_config):
        """New instance should have status=running, pid>0, home_dir exists."""
        mock_process = AsyncMock()
        mock_process.pid = 12345
        mock_process.returncode = None

        with patch("app.instance.asyncio.create_subprocess_exec",
                    return_value=mock_process):
            resp = app_client.post(
                "/api/instance/create", json={"user_id": "test1"}
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "running"
        home = mock_config.instance_base_dir / "test1"
        assert home.exists()


# ============================================================
# Test 2: Send prompt with SSE stream (mock)
# ============================================================
class TestPromptStream:
    def test_prompt_returns_sse_stream(self, app_client, mock_config):
        """Prompt should return SSE stream with text and done events."""
        claude_output_lines = [
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "text", "text": "Hello!"}
            ]}}),
            json.dumps({"type": "result", "subtype": "success"}),
        ]

        mock_process = AsyncMock()
        mock_process.pid = 99
        mock_process.returncode = None

        prompt_process = AsyncMock()
        prompt_process.pid = 100
        prompt_process.stdout = AsyncMock()
        prompt_process.stdout.readline = AsyncMock(
            side_effect=[
                (line + "\n").encode() for line in claude_output_lines
            ] + [b""]
        )
        prompt_process.wait = AsyncMock(return_value=0)

        call_count = 0

        async def fake_exec(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_process
            return prompt_process

        with patch("app.instance.asyncio.create_subprocess_exec",
                    side_effect=fake_exec):
            app_client.post(
                "/api/instance/create", json={"user_id": "test1"}
            )
            resp = app_client.post(
                "/api/instance/prompt",
                json={"user_id": "test1", "prompt": "say hello"},
                headers={"Accept": "text/event-stream"},
            )

        assert resp.status_code == 200
        body = resp.text
        assert "data:" in body
        assert '"type"' in body


# ============================================================
# Test 3: Query instance status
# ============================================================
class TestGetStatus:
    def test_status_running(self, app_client, mock_config):
        """Existing instance should return status=running."""
        mock_process = AsyncMock()
        mock_process.pid = 100
        mock_process.returncode = None

        with patch("app.instance.asyncio.create_subprocess_exec",
                    return_value=mock_process):
            app_client.post(
                "/api/instance/create", json={"user_id": "test1"}
            )

        resp = app_client.get("/api/instance/status/test1")
        assert resp.status_code == 200
        assert resp.json()["status"] == "running"


# ============================================================
# Test 4: Destroy instance
# ============================================================
class TestDestroyInstance:
    def test_destroy_returns_stopped(self, app_client, mock_config):
        """Destroyed instance status=stopped, home_dir preserved."""
        mock_process = AsyncMock()
        mock_process.pid = 100
        mock_process.returncode = None
        mock_process.terminate = MagicMock()
        mock_process.wait = AsyncMock(return_value=0)

        with patch("app.instance.asyncio.create_subprocess_exec",
                    return_value=mock_process):
            app_client.post(
                "/api/instance/create", json={"user_id": "test1"}
            )

        resp = app_client.post("/api/instance/destroy/test1")
        assert resp.status_code == 200
        assert resp.json()["status"] == "stopped"

        home = mock_config.instance_base_dir / "test1"
        assert home.exists()

        resp2 = app_client.get("/api/instance/status/test1")
        assert resp2.json()["status"] == "stopped"


# ============================================================
# Test 5: Duplicate create reuses instance
# ============================================================
class TestDuplicateCreate:
    def test_duplicate_create_reuses_instance(self, app_client, mock_config):
        """Same user create twice should reuse existing instance."""
        resp1 = app_client.post(
            "/api/instance/create", json={"user_id": "test1"}
        )
        session1 = resp1.json()["session_id"]

        resp2 = app_client.post(
            "/api/instance/create", json={"user_id": "test1"}
        )
        session2 = resp2.json()["session_id"]

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json()["status"] == "running"
        assert resp2.json()["status"] == "running"
        # Same session = same instance reused
        assert session1 == session2


# ============================================================
# Test 6: Nonexistent user returns stopped
# ============================================================
class TestNonexistentUser:
    def test_nonexistent_user_returns_stopped(self, app_client):
        """Nonexistent user status should be stopped."""
        resp = app_client.get("/api/instance/status/nonexist")
        assert resp.status_code == 200
        assert resp.json()["status"] == "stopped"


# ============================================================
# Test 7: Prompt timeout handling (mock)
# ============================================================
class TestPromptTimeout:
    def test_prompt_timeout_returns_error(self, app_client, mock_config):
        """Prompt timeout should return error, instance stays alive."""
        create_process = AsyncMock()
        create_process.pid = 200
        create_process.returncode = None

        prompt_process = AsyncMock()
        prompt_process.pid = 201
        prompt_process.stdout = AsyncMock()
        prompt_process.stdout.readline = AsyncMock(
            side_effect=asyncio.TimeoutError("timeout")
        )
        prompt_process.kill = MagicMock()
        prompt_process.wait = AsyncMock(return_value=-9)

        call_count = 0

        async def fake_exec(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return create_process
            return prompt_process

        with patch("app.instance.asyncio.create_subprocess_exec",
                    side_effect=fake_exec):
            app_client.post(
                "/api/instance/create", json={"user_id": "test1"}
            )
            resp = app_client.post(
                "/api/instance/prompt",
                json={"user_id": "test1", "prompt": "very long task"},
            )

        body = resp.text
        assert "error" in body.lower() or "timeout" in body.lower()

        status_resp = app_client.get("/api/instance/status/test1")
        assert status_resp.json()["status"] == "running"


# ============================================================
# Test 8: Crash auto-recovery (mock)
# ============================================================
class TestCrashRecovery:
    def test_crash_auto_restart(self, app_client, mock_config):
        """Crashed process should auto-restart on next prompt."""
        crashed_process = AsyncMock()
        crashed_process.pid = 300
        crashed_process.returncode = -9

        new_process = AsyncMock()
        new_process.pid = 301
        new_process.returncode = None
        new_process.stdout = AsyncMock()
        new_process.stdout.readline = AsyncMock(
            side_effect=[
                json.dumps(
                    {"type": "result", "subtype": "success"}
                ).encode() + b"\n",
                b"",
            ]
        )
        new_process.wait = AsyncMock(return_value=0)

        call_count = 0

        async def fake_exec(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return crashed_process
            return new_process

        with patch("app.instance.asyncio.create_subprocess_exec",
                    side_effect=fake_exec):
            app_client.post(
                "/api/instance/create", json={"user_id": "test1"}
            )

            from app.instance import InstanceManager
            inst = InstanceManager._instances.get("test1")
            if inst:
                inst._process = crashed_process

            resp = app_client.post(
                "/api/instance/prompt",
                json={"user_id": "test1", "prompt": "hello after crash"},
            )

        assert resp.status_code == 200


# ============================================================
# Test 9: Health check
# ============================================================
class TestHealthCheck:
    def test_health_returns_ok(self, app_client):
        """GET /health should return status=ok."""
        resp = app_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "instance-manager"
        assert "active_instances" in data
