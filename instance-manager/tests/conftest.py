"""Shared fixtures for instance-manager tests."""

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def temp_instance_dir(tmp_path):
    """Provide a temporary directory for instance data."""
    return tmp_path


@pytest.fixture
def mock_config(temp_instance_dir):
    """Config pointing to temp directory."""
    from app.config import Config
    return Config(
        claude_bin="/usr/bin/echo",  # Use echo as a safe mock
        claude_model="sonnet",
        claude_timeout_seconds=30,
        instance_base_dir=temp_instance_dir,
    )


@pytest.fixture
def app_client(mock_config):
    """TestClient with mocked config."""
    with patch("app.main.CONFIG", mock_config), \
         patch("app.instance.CONFIG", mock_config):
        from app.main import app
        with TestClient(app) as client:
            yield client


@pytest.fixture(autouse=True)
def clear_instances():
    """Clear instance registry between tests."""
    from app.instance import InstanceManager
    InstanceManager._instances.clear()
    yield
    InstanceManager._instances.clear()
