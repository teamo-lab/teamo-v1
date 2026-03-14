"""Shared fixtures for claude-code-proxy tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.proxy import _tasks


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clear_tasks():
    _tasks.clear()
    yield
    _tasks.clear()
