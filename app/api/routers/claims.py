from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import ClaimCreate, ClaimOut
from app.services.claim_service import create_claim

router = APIRouter()

@router.post("/api/cars/{carId}/claims", status_code=status.HTTP_201_CREATED, response_model=ClaimOut)
def register_claim(carId: int, payload: ClaimCreate, response: Response, db: Session = Depends(get_db)):
    claim = create_claim(
        db,
        car_id=carId,
        claim_date=payload.claim_date,
        description=payload.description,
        amount=payload.amount,
    )
    response.headers["Location"] = f"/api/cars/{carId}/claims/{claim.id}"
    return claim