# app/services/policy_service.py
from __future__ import annotations

from datetime import date
from typing import Optional

import structlog
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.db.models import Car, InsurancePolicy
from app.api.errors import CarNotFoundError, BadRequestError

log = structlog.get_logger()


def _ranges_overlap(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    """Inclusive range overlap: [a_start, a_end] vs [b_start, b_end]."""
    return not (a_end < b_start or a_start > b_end)


def assert_no_overlap(db: Session, car_id: int, start: date, end: date) -> None:
    """
    Check if any existing policy for this car overlaps [start, end].
    SQL form: NOT (existing.end < start OR existing.start > end)
    """
    overlap_stmt = (
        select(InsurancePolicy.id)
        .where(InsurancePolicy.car_id == car_id)
        .where(~( (InsurancePolicy.end_date < start) | (InsurancePolicy.start_date > end) ))
        .limit(1)
    )
    if db.execute(overlap_stmt).first():
        raise BadRequestError("Policy date range overlaps an existing policy.")


def create_policy(
    db: Session,
    car_id: int,
    provider: Optional[str],
    start_date: date,
    end_date: date,
) -> InsurancePolicy:
    # Car must exist
    car = db.get(Car, car_id)
    if not car:
        raise CarNotFoundError(car_id)

    # Date sanity
    if end_date < start_date:
        raise BadRequestError("endDate must be on or after startDate")

    # Overlap guard
    assert_no_overlap(db, car_id, start_date, end_date)

    # Create
    policy = InsurancePolicy(
        car_id=car_id,
        provider=provider,
        start_date=start_date,
        end_date=end_date,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)

    log.info(
        "policy_created",
        policyId=policy.id,
        carId=car_id,
        provider=provider,
        startDate=str(start_date),
        endDate=str(end_date),
    )
    return policy
