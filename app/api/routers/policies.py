from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import PolicyCreate, PolicyOut, ValidityOut
from app.services.policy_service import create_policy
from app.services.validity_service import is_insurance_valid_on
from app.utils.dates import parse_date_str
from app.api.errors import BadRequestError

router = APIRouter()

@router.post("/api/cars/{carId}/policies", status_code=status.HTTP_201_CREATED, response_model=PolicyOut)
def create_car_policy(carId: int, payload: PolicyCreate, db: Session = Depends(get_db)):
    policy = create_policy(
        db,
        car_id=carId,
        provider=payload.provider,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    return policy

@router.get("/api/cars/{carId}/insurance-valid", response_model=ValidityOut)
def insurance_valid(carId: int, date: str = Query(..., description="YYYY-MM-DD"), db: Session = Depends(get_db)):
    try:
        d = parse_date_str(date)
    except ValueError as e:
        raise BadRequestError(str(e))
    valid = is_insurance_valid_on(db, car_id=carId, on_date=d)
    return ValidityOut(car_id=carId, date=d, valid=valid)