"""
Usage Tracking Service for CloudEngineered Platform

Tracks per-user usage and enforces plan-based rate limits for:
- AI comparisons (free: 3/day, pro: unlimited)
- Comparison exports (free: blocked, pro: unlimited)
- AI searches (free: 5/day, pro: unlimited)
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Plan limits configuration
PLAN_LIMITS: Dict[str, Dict[str, int]] = {
    "free": {
        "comparisons": 3,
        "exports": 0,
        "ai_searches": 5,
    },
    "pro": {
        "comparisons": -1,  # unlimited
        "exports": -1,
        "ai_searches": -1,
    },
    "enterprise": {
        "comparisons": -1,
        "exports": -1,
        "ai_searches": -1,
    },
}


def get_plan_limit(plan: str, action: str) -> int:
    """Get the daily limit for an action on a given plan. -1 = unlimited."""
    plan_config = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    return plan_config.get(action, 0)


def check_and_increment_usage(db_session, user, action: str) -> Dict[str, Any]:
    """
    Check if user can perform an action, increment usage if allowed.

    Args:
        db_session: SQLAlchemy session
        user: User model instance
        action: Action type ("comparisons", "exports", "ai_searches")

    Returns:
        Dict with "allowed" bool, "remaining" count, "limit" count
    """
    from main import UsageLog

    plan = getattr(user, "subscription_plan", "free") or "free"
    limit = get_plan_limit(plan, action)

    # Unlimited
    if limit == -1:
        # Still log usage for analytics
        log = UsageLog(user_id=user.id, action=action)
        db_session.add(log)
        db_session.commit()
        return {"allowed": True, "remaining": -1, "limit": -1, "plan": plan}

    # Blocked entirely (e.g., exports on free plan)
    if limit == 0:
        return {"allowed": False, "remaining": 0, "limit": 0, "plan": plan, "upgrade_required": True}

    # Count today's usage
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = (
        db_session.query(UsageLog)
        .filter(
            UsageLog.user_id == user.id,
            UsageLog.action == action,
            UsageLog.created_at >= today_start,
        )
        .count()
    )

    if today_count >= limit:
        return {
            "allowed": False,
            "remaining": 0,
            "limit": limit,
            "plan": plan,
            "upgrade_required": True,
            "reset_at": (today_start + timedelta(days=1)).isoformat(),
        }

    # Log usage
    log = UsageLog(user_id=user.id, action=action)
    db_session.add(log)
    db_session.commit()

    return {
        "allowed": True,
        "remaining": limit - today_count - 1,
        "limit": limit,
        "plan": plan,
    }


def get_usage_summary(db_session, user) -> Dict[str, Any]:
    """Get usage summary for the current day."""
    from main import UsageLog

    plan = getattr(user, "subscription_plan", "free") or "free"
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    summary = {"plan": plan, "actions": {}}

    for action in ["comparisons", "exports", "ai_searches"]:
        limit = get_plan_limit(plan, action)
        today_count = (
            db_session.query(UsageLog)
            .filter(
                UsageLog.user_id == user.id,
                UsageLog.action == action,
                UsageLog.created_at >= today_start,
            )
            .count()
        )
        summary["actions"][action] = {
            "used": today_count,
            "limit": limit,
            "remaining": limit - today_count if limit > 0 else (-1 if limit == -1 else 0),
        }

    return summary
