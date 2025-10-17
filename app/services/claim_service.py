from datetime import datetime, timezone
from sqlalchemy.orm import Session
import structlog
from app.db.models import Car, Claim
from app.api.errors import CarNotFoundError

log = structlog.get_logger()

def create_claim(db: Session, car_id: int, claim_date, description: str, amount) -> Claim:
    car = db.get(Car, car_id)
    if not car:
        raise CarNotFoundError(car_id)

    claim = Claim(
        car_id=car_id,
        claim_date=claim_date,
        description=description,
        amount=amount,
        created_at=datetime.now(timezone.utc),
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)

    log.info(
        "claim_created",
        claimId=claim.id,
        carId=car_id,
        claimDate=str(claim_date),
        amount=str(amount)
    )
    return claim