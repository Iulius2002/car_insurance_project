from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.api.deps import get_db
from app.api.schemas import HistoryItem
from app.services.history_service import get_car_history


router = APIRouter()


@router.get("/api/cars/{carId}/history", response_model=List[HistoryItem])
def car_history(carId: int, db: Session = Depends(get_db)):
    return get_car_history(db, car_id=carId)