from app.db.session import SessionLocal
from app.db.models import Owner, Car
from datetime import date
from app.db.models import InsurancePolicy, Claim

if __name__ == "__main__":
    db = SessionLocal()
    try:
        alice = Owner(name="Alice", email="a@example.com")
        db.add(alice)
        db.flush()  # get alice.id

        c1 = Car(vin="WVWZZZ1JZXW000001", make="VW", model="Golf", year_of_manufacture=2018, owner=alice)
        c2 = Car(vin="WAUZZZ8V0HA000002", make="Audi", model="A3", year_of_manufacture=2017, owner=alice)
        db.add_all([c1, c2])
        db.commit()
        print("Seeded demo data.")
    finally:
        db.close()

# Simple timeline for car id 1
p1 = InsurancePolicy(car_id=1, provider="AXA", start_date=date(2024,1,1), end_date=date(2025,1,1))
p2 = InsurancePolicy(car_id=1, provider="Allianz", start_date=date(2025,1,2), end_date=date(2026,1,1))
c1 = Claim(car_id=1, claim_date=date(2024,5,10), description="Rear bumper", amount=450.00, created_at=__import__('datetime').datetime.utcnow())


from app.db.session import SessionLocal


if __name__ == "__main__":
    db = SessionLocal()
    try:
        # ... existing seed for owner/cars ...
        db.add_all([p1, p2, c1])
        db.commit()
        print("Seeded policies and claims.")
    finally:
        db.close()