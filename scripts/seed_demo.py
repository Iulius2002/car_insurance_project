from app.db.session import SessionLocal
from app.db.models import Owner, Car

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