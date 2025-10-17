# app/core/scheduling.py
from __future__ import annotations

from datetime import datetime, date, time, timedelta
from typing import Optional

import structlog
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import InsurancePolicy  # NOTE: exact casing matters

log = structlog.get_logger()

# Keep a single BackgroundScheduler instance
_scheduler: Optional[BackgroundScheduler] = None


def _within_window(now: datetime) -> bool:
    """Allow logging only in the first hour after midnight, unless TEST mode is on."""
    if settings.SCHEDULER_TEST_MODE:
        return True
    t = now.time()
    return time(0, 0) <= t < time(1, 0)


def detect_and_log_expired_policies(now: Optional[datetime] = None) -> int:
    """
    Find policies whose end_date was yesterday (inclusive validity), log once,
    and mark via logged_expiry_at to ensure idempotency. Returns count logged.
    """
    now = now or datetime.now()
    if not _within_window(now):
        return 0

    expired_on = (now.date() - timedelta(days=1))

    with SessionLocal() as db:
        stmt = (
            select(InsurancePolicy)
            .where(InsurancePolicy.end_date == expired_on)
            .where(InsurancePolicy.logged_expiry_at.is_(None))
        )
        policies = db.execute(stmt).scalars().all()

        for p in policies:
            log.info("policy_expired", policyId=p.id, carId=p.car_id, endDate=str(p.end_date))
            log.info("policy_expired_msg", message=f"Policy {p.id} for car {p.car_id} expired on {p.end_date}")
            p.logged_expiry_at = now

        if policies:
            db.commit()

        return len(policies)


def start_scheduler() -> None:
    """Create and start the background scheduler (interval = 10 min)."""
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        detect_and_log_expired_policies,
        trigger="interval",
        minutes=10,
        id="policy-expiry-logger",
        coalesce=True,
        max_instances=1,
        replace_existing=True,
    )
    _scheduler.start()
    log.info("scheduler_started", job_id="policy-expiry-logger")


def shutdown_scheduler() -> None:
    """Stop the scheduler on app shutdown."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        log.info("scheduler_stopped")
