from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
import structlog
from app.db.models import InsurancePolicy, Car
from app.api.errors import CarNotFoundError

log = structlog.get_logger()

def is_insurance_valid_on(db: Session, car_id: int, on_date: date) -> bool:
    car = db.get(Car, car_id)
    if not car:
        raise CarNotFoundError(car_id)

    stmt = (
        select(InsurancePolicy.id)
        .where(InsurancePolicy.car_id == car_id)
        .where(InsurancePolicy.start_date <= on_date)
        .where(InsurancePolicy.end_date >= on_date)
        .limit(1)
    )
    res = db.execute(stmt).first()
    valid = res is not None
    log.info("insurance_validity_checked", carId=car_id, date=str(on_date), valid=valid)
    return valid