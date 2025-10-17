from datetime import date
from sqlalchemy.orm import Session
import structlog
from app.db.models import Car, InsurancePolicy
from app.api.errors import CarNotFoundError, BadRequestError

log = structlog.get_logger()

def create_policy(
    db: Session,
    car_id: int,
    provider: str | None,
    start_date: date,
    end_date: date
) -> InsurancePolicy:
    car = db.get(Car, car_id)
    if not car:
        raise CarNotFoundError(car_id)

    if end_date < start_date:
        raise BadRequestError("endDate must be on or after startDate")

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
        endDate=str(end_date)
    )
    return policy