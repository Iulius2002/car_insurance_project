from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import SessionLocal

# Dependency to be used in routes
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()