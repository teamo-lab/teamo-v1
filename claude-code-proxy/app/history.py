"""Conversation history persistence via MongoDB."""

import logging
from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import CONFIG

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_db = None


def get_db():
    """Get or create the MongoDB database handle."""
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(CONFIG.mongodb_uri)
        _db = _client[CONFIG.mongodb_db]
    return _db


async def save_conversation(
    conv_id: str,
    session_group_id: str,
    username: str,
    query: str,
    response: str,
    mode: str = "claude_code",
) -> None:
    """Save a conversation turn (question + answer) to MongoDB."""
    db = get_db()
    doc = {
        "conv_id": conv_id,
        "session_group_id": session_group_id,
        "username": username,
        "query": query,
        "response": response,
        "mode": mode,
        "battery_cost": 0,
        "request_time": datetime.utcnow(),
    }
    try:
        await db.claude_code_conversations.insert_one(doc)
        logger.info("Saved conversation %s for user %s", conv_id, username)
    except Exception:
        logger.exception("Failed to save conversation %s", conv_id)
