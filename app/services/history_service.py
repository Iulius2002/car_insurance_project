from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Car, InsurancePolicy, Claim
from app.api.errors import CarNotFoundError


def get_car_history(db: Session, car_id: int) -> list[dict]:
    car = db.get(Car, car_id)
    if not car:
        raise CarNotFoundError(car_id)

    policies = db.execute(
        select(InsurancePolicy)
        .where(InsurancePolicy.car_id == car_id)
        .order_by(InsurancePolicy.start_date)
    ).scalars().all()

    claims = db.execute(
        select(Claim)
        .where(Claim.car_id == car_id)
        .order_by(Claim.claim_date)
    ).scalars().all()

    events: list[dict] = []

    for p in policies:
        events.append({
            "type": "POLICY",
            "policy_id": p.id,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "provider": p.provider,
            "_sort": p.start_date,
        })

    for c in claims:
        events.append({
            "type": "CLAIM",
            "claim_id": c.id,
            "claim_date": c.claim_date,
            "amount": c.amount,
            "description": c.description,
            "_sort": c.claim_date,
        })

    events.sort(key=lambda e: e["_sort"])  # ascending chronological order
    for e in events:
        e.pop("_sort", None)

    return events
