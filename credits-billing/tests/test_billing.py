"""Unit tests for Credits Billing system.

Test plan: docs/05-test-plan/credits-billing-tests.md
8 test cases covering daily billing, insufficient balance, boundary,
priority deduction, balance query, warning, recharge recovery.
"""

import pytest

from app.billing import check_and_bill, deduct_credits, get_credits_info
from app.models import DAILY_COST, UserCredits


# ============================================================
# Test 1: Normal daily billing
# ============================================================
class TestNormalBilling:
    def test_deduct_28_from_100(self):
        """User with 100 credits: deduct 28, remaining 72."""
        user = UserCredits(user_id="u1", remain_extend_battery=100)
        result = check_and_bill(user)

        assert result.deducted == 28
        assert result.stopped is False
        assert result.remaining == 72
        assert user.remain_extend_battery == 72


# ============================================================
# Test 2: Insufficient balance stops instance
# ============================================================
class TestInsufficientBalance:
    def test_balance_20_stops_instance(self):
        """User with 20 credits: do NOT deduct, stop instance."""
        user = UserCredits(user_id="u2", remain_extend_battery=20)
        result = check_and_bill(user)

        assert result.deducted == 0
        assert result.stopped is True
        assert result.remaining == 20
        # Credits untouched
        assert user.remain_extend_battery == 20


# ============================================================
# Test 3: Boundary — exactly 28 credits
# ============================================================
class TestExactBoundary:
    def test_exactly_28_deducts_to_zero(self):
        """User with exactly 28 credits: deduct all, instance stays running."""
        user = UserCredits(user_id="u3", remain_extend_battery=28)
        result = check_and_bill(user)

        assert result.deducted == 28
        assert result.stopped is False
        assert result.remaining == 0
        assert user.remain_extend_battery == 0


# ============================================================
# Test 4: Balance = 0, already stopped
# ============================================================
class TestZeroBalance:
    def test_zero_balance_noop(self):
        """User with 0 credits: no deduction, no repeated stop."""
        user = UserCredits(user_id="u4")
        result = check_and_bill(user)

        assert result.deducted == 0
        assert result.stopped is False  # Not stopping again
        assert result.remaining == 0


# ============================================================
# Test 5: Deduction priority order
# ============================================================
class TestDeductionPriority:
    def test_priority_free_vip_extend(self):
        """free=10, vip=10, extend=50 -> deduct 28 -> free=0, vip=0, extend=42."""
        user = UserCredits(
            user_id="u5",
            remain_free_battery=10,
            remain_vip_battery=10,
            remain_extend_battery=50,
        )
        result = check_and_bill(user)

        assert result.deducted == 28
        assert user.remain_free_battery == 0
        assert user.remain_vip_battery == 0
        assert user.remain_extend_battery == 42
        assert result.remaining == 42

    def test_priority_partial_free(self):
        """free=30, vip=0, extend=0 -> deduct 28 -> free=2."""
        user = UserCredits(
            user_id="u5b",
            remain_free_battery=30,
        )
        result = check_and_bill(user)

        assert user.remain_free_battery == 2
        assert result.deducted == 28


# ============================================================
# Test 6: Credits info query
# ============================================================
class TestCreditsInfo:
    def test_credits_info_correct(self):
        """credits=156 -> total=156, daily=28, days=5."""
        user = UserCredits(user_id="u6", remain_extend_battery=156)
        info = get_credits_info(user)

        assert info["total_credits"] == 156
        assert info["daily_cost"] == 28
        assert info["estimated_days"] == 5
        assert info["warning"] is None


# ============================================================
# Test 7: Low balance warning
# ============================================================
class TestLowBalanceWarning:
    def test_warning_when_less_than_3_days(self):
        """credits=56 (2 days) -> warning non-empty."""
        user = UserCredits(user_id="u7", remain_extend_battery=56)
        info = get_credits_info(user)

        assert info["warning"] is not None
        assert "不足" in info["warning"]

    def test_no_warning_when_sufficient(self):
        """credits=200 -> no warning."""
        user = UserCredits(user_id="u7b", remain_extend_battery=200)
        info = get_credits_info(user)

        assert info["warning"] is None

    def test_warning_zero_credits(self):
        """credits=0 -> warning mentions stopped."""
        user = UserCredits(user_id="u7c")
        info = get_credits_info(user)

        assert info["warning"] is not None
        assert "停机" in info["warning"]


# ============================================================
# Test 8: Recharge recovery check
# ============================================================
class TestRechargeRecovery:
    def test_after_recharge_can_bill(self):
        """After recharging from 0 to 100, billing should work."""
        user = UserCredits(user_id="u8")
        # Initial state: 0 credits
        result1 = check_and_bill(user)
        assert result1.remaining == 0

        # Simulate recharge
        user.remain_extend_battery = 100

        # Now billing should succeed
        result2 = check_and_bill(user)
        assert result2.deducted == 28
        assert result2.stopped is False
        assert result2.remaining == 72
