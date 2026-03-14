"""Core billing logic for Credits system."""

import logging
from typing import Callable, Coroutine, List, Optional

from app.models import DAILY_COST, BillingResult, UserCredits

logger = logging.getLogger(__name__)


def deduct_credits(user: UserCredits, amount: float) -> float:
    """Deduct credits in priority order: free -> vip -> extend.

    Returns the actual amount deducted.
    """
    remaining = amount
    deducted = 0.0

    # Priority 1: free battery
    if remaining > 0 and user.remain_free_battery > 0:
        take = min(user.remain_free_battery, remaining)
        user.remain_free_battery -= take
        remaining -= take
        deducted += take

    # Priority 2: vip battery
    if remaining > 0 and user.remain_vip_battery > 0:
        take = min(user.remain_vip_battery, remaining)
        user.remain_vip_battery -= take
        remaining -= take
        deducted += take

    # Priority 3: extend battery
    if remaining > 0 and user.remain_extend_battery > 0:
        take = min(user.remain_extend_battery, remaining)
        user.remain_extend_battery -= take
        remaining -= take
        deducted += take

    return deducted


def check_and_bill(user: UserCredits) -> BillingResult:
    """Check user balance and deduct daily cost, or stop instance.

    Business rules:
    - If total < DAILY_COST: do NOT deduct, stop instance
    - If total >= DAILY_COST: deduct in priority order
    - If total == 0 and already stopped: no-op
    """
    total = user.total
    result = BillingResult(user_id=user.user_id)

    if total <= 0:
        result.message = "余额为 0，已停机"
        result.remaining = 0
        return result

    if total < DAILY_COST:
        result.stopped = True
        result.remaining = total
        result.message = "余额不足，停机"
        return result

    deducted = deduct_credits(user, DAILY_COST)
    result.deducted = deducted
    result.remaining = user.total
    result.message = "扣费成功"
    return result


def get_credits_info(user: UserCredits) -> dict:
    """Get credits info for API response."""
    return {
        "total_credits": user.total,
        "daily_cost": DAILY_COST,
        "estimated_days": user.estimated_days,
        "warning": user.warning,
        "breakdown": {
            "free": user.remain_free_battery,
            "vip": user.remain_vip_battery,
            "extend": user.remain_extend_battery,
        },
    }
