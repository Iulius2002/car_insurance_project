from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.schemas import CarOut
from app.api.deps import get_db
from app.db.models import Car

router = APIRouter()

@router.get("/api/cars", response_model=List[CarOut])
def list_cars(db: Session = Depends(get_db)):
    stmt = select(Car).options(selectinload(Car.owner)).order_by(Car.id)
    cars = db.execute(stmt).scalars().all()
    # FastAPI+pydantic v2 will serialize using aliases for fields with serialization_alias
    return cars