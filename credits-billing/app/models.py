"""Models for Credits Billing system."""

from dataclasses import dataclass
from typing import Optional


DAILY_COST = 28
WARNING_THRESHOLD = 84  # 3 days
NEW_USER_CREDITS = 100


@dataclass
class UserCredits:
    user_id: str
    remain_free_battery: float = 0
    remain_vip_battery: float = 0
    remain_extend_battery: float = 0

    @property
    def total(self) -> float:
        return self.remain_free_battery + self.remain_vip_battery + self.remain_extend_battery

    @property
    def estimated_days(self) -> int:
        if DAILY_COST == 0:
            return 999
        return int(self.total // DAILY_COST)

    @property
    def warning(self) -> Optional[str]:
        if self.total <= 0:
            return "余额为 0，实例已停机"
        if self.total < WARNING_THRESHOLD:
            days = self.estimated_days
            return f"余额不足 {days} 天，请及时充值"
        return None


@dataclass
class BillingResult:
    user_id: str
    deducted: float = 0
    stopped: bool = False
    remaining: float = 0
    message: str = ""
