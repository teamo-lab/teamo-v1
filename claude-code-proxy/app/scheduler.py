"""Daily billing scheduler for Claude Code instances.

Runs as an asyncio background task within the proxy service.
Every day at UTC 00:00, queries MongoDB for users with running instances
and deducts credits. Stops instances when credits are insufficient.
"""

import asyncio
import logging
from datetime import datetime, timezone

import httpx

from app.config import CONFIG
from app.history import get_db

logger = logging.getLogger(__name__)

DAILY_COST = 28


async def _run_daily_billing() -> dict:
    """Execute one billing cycle for all running instances.

    Returns a summary dict with counts.
    """
    db = get_db()
    summary = {"billed": 0, "stopped": 0, "errors": 0}

    # Find users with running instances by querying instance-manager
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{CONFIG.instance_manager_url}/api/instances"
            )
            if resp.status_code != 200:
                logger.warning("Cannot list instances: %s", resp.status_code)
                return summary
            instances = resp.json()
    except httpx.HTTPError as exc:
        logger.exception("Cannot reach instance-manager: %s", exc)
        return summary

    for inst in instances:
        user_id = inst.get("user_id", "")
        if not user_id:
            continue

        try:
            # Get user credits from MongoDB (wowchat users collection)
            user_doc = await db.users.find_one({"username": user_id})
            if not user_doc:
                logger.warning("User %s not found in MongoDB, skipping", user_id)
                continue

            total = (
                user_doc.get("remain_free_battery", 0)
                + user_doc.get("remain_vip_battery", 0)
                + user_doc.get("remain_extend_battery", 0)
            )

            if total < DAILY_COST:
                # Insufficient credits — stop instance
                logger.info("User %s has %.0f credits (< %d), stopping", user_id, total, DAILY_COST)
                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        await client.post(
                            f"{CONFIG.instance_manager_url}/api/instance/destroy/{user_id}"
                        )
                except httpx.HTTPError:
                    logger.exception("Failed to stop instance for %s", user_id)
                summary["stopped"] += 1
                continue

            # Deduct credits in priority order: free → vip → extend
            remaining = DAILY_COST
            updates = {}

            for field in ["remain_free_battery", "remain_vip_battery", "remain_extend_battery"]:
                avail = user_doc.get(field, 0)
                if remaining <= 0 or avail <= 0:
                    continue
                take = min(avail, remaining)
                updates[field] = avail - take
                remaining -= take

            if updates:
                await db.users.update_one(
                    {"username": user_id},
                    {"$set": updates},
                )
                logger.info("Billed user %s: deducted %d credits", user_id, DAILY_COST)
                summary["billed"] += 1

        except Exception:
            logger.exception("Billing error for user %s", user_id)
            summary["errors"] += 1

    return summary


async def _scheduler_loop():
    """Run billing daily at UTC 00:00."""
    logger.info("Billing scheduler started")
    while True:
        now = datetime.now(timezone.utc)
        # Calculate seconds until next UTC 00:00
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now >= tomorrow:
            # Already past midnight today, schedule for tomorrow
            tomorrow = tomorrow.replace(day=now.day + 1)
            # Handle month rollover via timedelta
            from datetime import timedelta
            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        wait_seconds = (tomorrow - now).total_seconds()
        logger.info("Next billing in %.0f seconds (at %s UTC)", wait_seconds, tomorrow.isoformat())

        await asyncio.sleep(wait_seconds)

        logger.info("Running daily billing cycle")
        try:
            summary = await _run_daily_billing()
            logger.info("Billing complete: %s", summary)
        except Exception:
            logger.exception("Billing cycle failed")


_scheduler_task = None


def start_scheduler():
    """Start the billing scheduler as a background task."""
    global _scheduler_task
    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = asyncio.create_task(_scheduler_loop())
        logger.info("Billing scheduler task created")


def stop_scheduler():
    """Cancel the billing scheduler."""
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        logger.info("Billing scheduler cancelled")


# Expose for testing
run_daily_billing = _run_daily_billing
