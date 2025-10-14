from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Date, DateTime, ForeignKey, Integer, Numeric, String, Text,
    UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

# --- Owner ---
class Owner(Base):
    __tablename__ = "owner"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    cars: Mapped[List["Car"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

# --- Car ---
class Car(Base):
    __tablename__ = "car"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vin: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    make: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    year_of_manufacture: Mapped[Optional[int]] = mapped_column(Integer)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("owner.id", ondelete="RESTRICT"), nullable=False
    )
    owner: Mapped[Owner] = relationship(back_populates="cars")
    policies: Mapped[List["InsurancePolicy"]] = relationship(
        back_populates="car", cascade="all, delete-orphan"
    )
    claims: Mapped[List["Claim"]] = relationship(
        back_populates="car", cascade="all, delete-orphan"
    )

# --- Insurance Policy ---
class InsurancePolicy(Base):
    __tablename__ = "insurance_policy"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    car_id: Mapped[int] = mapped_column(
        ForeignKey("car.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[Optional[str]] = mapped_column(String(120))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Final business state: NOT NULL. We'll demonstrate a data migration to reach that.
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Optional: track expiry logging once-only
    logged_expiry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    car: Mapped[Car] = relationship(back_populates="policies")
    __table_args__ = (
        Index("ix_policy_car_dates", "car_id", "start_date", "end_date"),
    )

# --- Claim ---
class Claim(Base):
    __tablename__ = "claim"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    car_id: Mapped[int] = mapped_column(
        ForeignKey("car.id", ondelete="CASCADE"), nullable=False
    )
    claim_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    car: Mapped[Car] = relationship(back_populates="claims")
    __table_args__ = (
        Index("ix_claim_car_date", "car_id", "claim_date"),
    )
