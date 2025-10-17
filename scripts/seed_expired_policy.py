from datetime import date, timedelta
from app.db.session import SessionLocal
from app.db.models import InsurancePolicy


if __name__ == "__main__":
    db = SessionLocal()
    try:
        car_id = 1  # adjust if needed
        yesterday = date.today() - timedelta(days=1)
        policy = InsurancePolicy(
            car_id=car_id,
            provider="DevSeed",
            start_date=yesterday - timedelta(days=365),
            end_date=yesterday,
        )
        db.add(policy)
        db.commit()
        print(f"Seeded expired policy id={policy.id} for car {car_id}, end_date={policy.end_date}")
    finally:
        db.close()
