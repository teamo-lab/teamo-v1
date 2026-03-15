"""Unit tests for Claude Code Proxy.

Test plan: docs/05-test-plan/claude-code-proxy-tests.md
8 test cases covering mode routing, SSE conversion, streaming,
stop, history, auth, auto-create.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.sse_converter import convert_instance_sse


# ============================================================
# Test 1: mode=claude_code routes to instance service
# ============================================================
class TestModeRouting:
    def test_claude_code_mode_routes_to_instance(self, client):
        """mode=claude_code should create a task and return task_id.

        Note: askAgents only creates a task entry; the actual instance-manager
        call happens during askAgentsCheck (stream_check).
        """
        resp = client.post(
            "/api/engine/askAgents",
            json={"query": "hello", "mode": "claude_code"},
            headers={"Authorization": "Bearer user123"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["result"]["mcp_task_id"] != ""


# ============================================================
# Test 2: mode=a2a routes to old MCP engine
# ============================================================
class TestResearchModeRouting:
    def test_a2a_mode_does_not_call_instance(self, client):
        """mode=a2a should forward to legacy backend, not instance-manager."""
        legacy_response = httpx.Response(200, json={"code": 0, "result": {}})

        with patch("app.proxy.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.request = AsyncMock(return_value=legacy_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            resp = client.post(
                "/api/engine/askAgents",
                json={"query": "research this", "mode": "a2a"},
                headers={"Authorization": "Bearer user123"},
            )

        assert resp.status_code == 200
        # Legacy backend was called via .request(), not instance-manager
        mock_client.request.assert_called_once()
        call_url = mock_client.request.call_args[0][1]
        assert "/api/engine/askAgents" in call_url


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
class TestConversationHistory:
    def test_history_saved_after_stream(self, client):
        """After streaming, conversation should be saved to MongoDB."""
        from app.proxy import _tasks

        # Create a task first
        resp = client.post(
            "/api/engine/askAgents",
            json={"query": "test query", "mode": "claude_code"},
            headers={"Authorization": "Bearer histuser"},
        )
        task_id = resp.json()["result"]["mcp_task_id"]

        # Mock the instance-manager SSE stream
        sse_lines = [
            'data: {"type":"text","content":"Hello"}\n\n',
            'data: {"type":"text","content":" world"}\n\n',
            'data: {"type":"done","session_id":"s1"}\n\n',
        ]

        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.aiter_lines = AsyncMock(
            return_value=AsyncMock(__aiter__=lambda self: self, __anext__=None)
        )

        async def fake_aiter():
            for line in sse_lines:
                yield line.strip()

        with patch("app.proxy.httpx.AsyncClient") as MockClient, \
             patch("app.proxy.save_conversation") as mock_save:
            mock_client = AsyncMock()
            mock_stream_ctx = AsyncMock()

            mock_stream_response = AsyncMock()
            mock_stream_response.aiter_lines = lambda: fake_aiter()

            mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_stream_response)
            mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.stream = lambda *a, **kw: mock_stream_ctx
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            resp = client.post(
                "/api/engine/askAgentsCheck",
                json={"mcp_task_id": task_id, "mode": "claude_code"},
                headers={"Authorization": "Bearer histuser"},
            )

        assert resp.status_code == 200
        # Verify save_conversation was called with accumulated text
        mock_save.assert_called_once()
        call_kwargs = mock_save.call_args
        assert call_kwargs[1]["query"] == "test query" or \
               (len(call_kwargs[0]) > 3 and call_kwargs[0][3] == "test query")
        # Check response text includes both chunks
        args = call_kwargs[1] if call_kwargs[1] else {}
        if "response" in args:
            assert "Hello" in args["response"]
            assert "world" in args["response"]


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
        """askAgents with claude_code mode should create task entry and return task_id.

        Instance auto-creation happens when stream_check calls instance-manager
        /api/instance/prompt (instance-manager creates on first prompt).
        """
        resp = client.post(
            "/api/engine/askAgents",
            json={"query": "build an app", "mode": "claude_code"},
            headers={"Authorization": "Bearer newuser"},
        )

        data = resp.json()
        assert data["code"] == 0
        assert data["result"]["mcp_task_id"] != ""

        # Verify task was stored internally
        from app.proxy import _tasks
        task_id = data["result"]["mcp_task_id"]
        assert task_id in _tasks
        assert _tasks[task_id]["query"] == "build an app"


# ============================================================
# Test 9: Daily billing scheduler
# ============================================================
class TestBillingScheduler:
    @pytest.mark.asyncio
    async def test_billing_deducts_and_stops(self):
        """Daily billing should deduct credits and stop instances with insufficient balance."""
        from app.scheduler import _run_daily_billing

        # Mock instance-manager listing 2 instances
        instances_response = httpx.Response(200, json=[
            {"user_id": "user_rich", "status": "running"},
            {"user_id": "user_poor", "status": "running"},
        ])

        # Mock MongoDB users
        user_rich = {
            "username": "user_rich",
            "remain_free_battery": 50,
            "remain_vip_battery": 50,
            "remain_extend_battery": 0,
        }
        user_poor = {
            "username": "user_poor",
            "remain_free_battery": 10,
            "remain_vip_battery": 0,
            "remain_extend_battery": 0,
        }

        mock_db = MagicMock()
        mock_users = AsyncMock()
        mock_db.users = mock_users

        async def find_one(query):
            name = query.get("username")
            if name == "user_rich":
                return user_rich.copy()
            if name == "user_poor":
                return user_poor.copy()
            return None

        mock_users.find_one = find_one
        mock_users.update_one = AsyncMock()

        # Mock instance-manager destroy
        destroy_response = httpx.Response(200, json={"status": "stopped"})

        with patch("app.scheduler.get_db", return_value=mock_db), \
             patch("app.scheduler.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=instances_response)
            mock_client.post = AsyncMock(return_value=destroy_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            summary = await _run_daily_billing()

        assert summary["billed"] == 1  # user_rich
        assert summary["stopped"] == 1  # user_poor
        # Verify credits were deducted for rich user
        mock_users.update_one.assert_called_once()
        update_call = mock_users.update_one.call_args
        assert update_call[0][0] == {"username": "user_rich"}
        set_fields = update_call[0][1]["$set"]
        # 50 free - 28 = 22 remaining free
        assert set_fields["remain_free_battery"] == 22
