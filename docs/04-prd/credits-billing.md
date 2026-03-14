# Credits 计费系统 PRD

> Phase 4 | 模块: credits-billing | 创建时间: 2026-03-15

## 模块概述

管理 Claude Code 实例的按天计费逻辑。1 credit = 0.035 元，实例运行费用约 28 credits/天。

## 用户故事

- 作为用户，我希望清楚知道每天花多少 credits
- 作为系统，我需要在 credits 为 0 时自动停止实例
- 作为用户，我希望充值后实例自动恢复运行

## 功能清单

| # | 功能 | 优先级 | MVP | 描述 |
|---|------|--------|-----|------|
| 1 | 每日扣费 | P0 | Yes | 定时任务每日扣除 28 credits |
| 2 | 余额检查 | P0 | Yes | 扣费前检查余额，不足则停机 |
| 3 | 余额查询 | P1 | Yes | API 查询剩余 credits 和预估天数 |
| 4 | 停机通知 | P1 | Yes | 余额不足 3 天时提醒，为 0 时通知已停机 |
| 5 | 充值恢复 | P1 | Yes | 充值后自动恢复实例运行 |

## 计费规则

```
1 credit = 0.035 元（人民币）
实例日费 = 28 credits/天（≈ 1 元/天）
扣费时间 = 每日 UTC 00:00
扣费对象 = 所有 status='running' 的实例
```

### 扣费优先级（复用现有电池体系）
1. remain_free_battery（免费额度）
2. remain_vip_battery（VIP 额度）
3. remain_extend_battery（充值额度）

### 停机逻辑
```python
async def daily_billing_task():
    """定时任务：每日扣费"""
    instances = await get_running_instances()
    for instance in instances:
        user = await get_user(instance.user_id)
        total_credits = (user.remain_free_battery +
                        user.remain_vip_battery +
                        user.remain_extend_battery)

        if total_credits < 28:
            # 余额不足，停机
            await stop_instance(instance.user_id)
            await notify_user(instance.user_id, "credits_exhausted")
        else:
            # 正常扣费
            await deduct_credits(instance.user_id, 28)
```

## API 设计

### GET /api/engine/creditsInfo
```json
Response:
{
  "code": 0,
  "result": {
    "total_credits": 156,
    "daily_cost": 28,
    "estimated_days": 5,
    "instance_status": "running",
    "next_billing": "2026-03-16T00:00:00Z",
    "warning": null  // or "余额不足 3 天"
  }
}
```

## 业务规则

- 新注册用户赠送 100 credits（约 3.5 天体验）
- 每日 UTC 00:00 执行扣费
- 余额 < 84 credits（3 天）时前端显示警告
- 余额 < 28 credits（1 天）时发送通知
- 余额 = 0 时立即停机，不等到下一个扣费周期
- 用户无法手动停机（按需求确认）
- 充值后如有已停机的实例，自动恢复（需余额 >= 28）
