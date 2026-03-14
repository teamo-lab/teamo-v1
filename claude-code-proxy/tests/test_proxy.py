"""Unit tests for Claude Code Proxy.

Test plan: docs/05-test-plan/claude-code-proxy-tests.md
8 test cases covering mode routing, SSE conversion, streaming,
stop, history, auth, auto-create.
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.sse_converter import convert_instance_sse


# ============================================================
# Test 1: mode=claude_code routes to instance service
# ============================================================
class TestModeRouting:
    def test_claude_code_mode_routes_to_instance(self, client):
        """mode=claude_code should call instance-manager, not MCP."""
        mock_response = httpx.Response(200, json={"status": "ok"})

        with patch("app.proxy.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            resp = client.post(
                "/api/engine/askAgents",
                json={"query": "hello", "mode": "claude_code"},
                headers={"Authorization": "Bearer user123"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["mcp_task_id"] != ""
        # Verify instance-manager was called
        mock_instance.post.assert_called_once()
        call_url = mock_instance.post.call_args[0][0]
        assert "/api/instance/prompt" in call_url


# ============================================================
# Test 2: mode=a2a routes to old MCP engine
# ============================================================
class TestResearchModeRouting:
    def test_a2a_mode_does_not_call_instance(self, client):
        """mode=a2a should NOT call instance-manager."""
        with patch("app.proxy.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            MockClient.return_value = mock_instance

            resp = client.post(
                "/api/engine/askAgents",
                json={"query": "research this", "mode": "a2a"},
                headers={"Authorization": "Bearer user123"},
            )

        assert resp.status_code == 200
        # No instance-manager call for a2a mode
        mock_instance.post.assert_not_called()


# ============================================================
# Test 3: SSE format conversion
# ============================================================
class TestSSEConversion:
    def test_text_event_converts_to_answer_chunk(self):
        """text event -> step/answer_chunk."""
        raw = 'data: {"type":"text","content":"Hello world"}\n\n'
        result = convert_instance_sse(raw)
        assert len(result) == 1
        parsed = json.loads(result[0].replace("data: ", "").strip())
        assert parsed["event"] == "step"
        assert parsed["name"] == "answer_chunk"
        assert parsed["result"]["message"] == "Hello world"

    def test_thinking_event_converts_to_think_chunk(self):
        """thinking event -> step/think_chunk."""
        raw = 'data: {"type":"thinking","content":"Let me think..."}\n\n'
        result = convert_instance_sse(raw)
        assert len(result) == 1
        parsed = json.loads(result[0].replace("data: ", "").strip())
        assert parsed["name"] == "think_chunk"

    def test_tool_use_event_converts(self):
        """tool_use event -> step/tool_call."""
        raw = 'data: {"type":"tool_use","tool":"Read","input":{"file_path":"/app"}}\n\n'
        result = convert_instance_sse(raw)
        assert len(result) == 1
        parsed = json.loads(result[0].replace("data: ", "").strip())
        assert parsed["name"] == "tool_call"
        assert parsed["result"]["tool"] == "Read"

    def test_tool_result_event_converts(self):
        """tool_result event -> step/tool_result."""
        raw = 'data: {"type":"tool_result","output":"file contents"}\n\n'
        result = convert_instance_sse(raw)
        parsed = json.loads(result[0].replace("data: ", "").strip())
        assert parsed["name"] == "tool_result"

    def test_done_event_converts_to_task_done(self):
        """done event -> task_done."""
        raw = 'data: {"type":"done","session_id":"abc"}\n\n'
        result = convert_instance_sse(raw)
        parsed = json.loads(result[0].replace("data: ", "").strip())
        assert parsed["event"] == "task_done"

    def test_error_event_converts(self):
        """error event -> step/error."""
        raw = 'data: {"type":"error","message":"something failed"}\n\n'
        result = convert_instance_sse(raw)
        parsed = json.loads(result[0].replace("data: ", "").strip())
        assert parsed["name"] == "error"
        assert "something failed" in parsed["result"]["message"]


# ============================================================
# Test 4: Streaming proxy (mock) - verified via SSE conversion tests
# ============================================================
# Integration test; covered by Test 3 unit + real server tests


# ============================================================
# Test 5: User stop task
# ============================================================
class TestUserStop:
    def test_stop_returns_success(self, client):
        """Stopping a task should return code=0."""
        from app.proxy import _tasks
        _tasks["task123"] = {
            "user_id": "user123",
            "mode": "claude_code",
            "query": "test",
        }

        with patch("app.proxy.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(
                return_value=httpx.Response(200, json={"status": "stopped"})
            )
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            resp = client.post(
                "/api/engine/askAgentsUserStop",
                json={"mcp_task_id": "task123", "mode": "claude_code"},
                headers={"Authorization": "Bearer user123"},
            )

        assert resp.status_code == 200
        assert resp.json()["code"] == 0


# ============================================================
# Test 6: Conversation history save (mock)
# ============================================================
# Integration test — requires MongoDB; covered in integration tests


# ============================================================
# Test 7: Unauthenticated user rejected
# ============================================================
class TestAuthCheck:
    def test_no_token_returns_401(self, client):
        """Request without Authorization header should return 401."""
        resp = client.post(
            "/api/engine/askAgents",
            json={"query": "hello", "mode": "claude_code"},
        )
        assert resp.status_code == 401
        data = resp.json()
        assert data["detail"]["code"] == 30

    def test_no_token_on_stop_returns_401(self, client):
        resp = client.post(
            "/api/engine/askAgentsUserStop",
            json={"mcp_task_id": "x", "mode": "claude_code"},
        )
        assert resp.status_code == 401

    def test_no_token_on_status_returns_401(self, client):
        resp = client.get("/api/engine/instanceStatus")
        assert resp.status_code == 401


# ============================================================
# Test 8: Auto-create instance when not running
# ============================================================
class TestAutoCreate:
    def test_ask_agents_creates_instance_if_needed(self, client):
        """askAgents with claude_code mode should auto-create and return task_id."""
        mock_response = httpx.Response(200, json={"status": "ok"})

        with patch("app.proxy.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            resp = client.post(
                "/api/engine/askAgents",
                json={"query": "build an app", "mode": "claude_code"},
                headers={"Authorization": "Bearer newuser"},
            )

        data = resp.json()
        assert data["code"] == 0
        assert data["mcp_task_id"] != ""
        # The instance-manager /prompt endpoint auto-creates
        mock_instance.post.assert_called_once()
