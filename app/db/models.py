# app/db/models.py
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Owner(Base):
    __tablename__ = "owner"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # relationships
    cars: Mapped[list["Car"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Car(Base):
    __tablename__ = "car"

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(String(17), nullable=False, unique=True)
    make: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    year_of_manufacture: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owner.id", ondelete="RESTRICT"), nullable=False)

    # relationships
    owner: Mapped["Owner"] = relationship(back_populates="cars")
    policies: Mapped[list["InsurancePolicy"]] = relationship(
        back_populates="car",
        cascade="all, delete-orphan",
    )
    claims: Mapped[list["Claim"]] = relationship(       # <-- must match Claim.car
        back_populates="car",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_car_vin", "vin", unique=True),
    )


class InsurancePolicy(Base):
    __tablename__ = "insurance_policy"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("car.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    # used by scheduler idempotency
    logged_expiry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # relationships
    car: Mapped["Car"] = relationship(back_populates="policies")

    __table_args__ = (
        Index("ix_policy_car_dates", "car_id", "start_date", "end_date"),
    )


class Claim(Base):
    __tablename__ = "claim"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("car.id", ondelete="CASCADE"), nullable=False)
    claim_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # DB default so direct inserts in tests don’t fail
    )

    # relationships
    car: Mapped["Car"] = relationship(back_populates="claims")  # <-- this was missing

    __table_args__ = (
        Index("ix_claim_car_date", "car_id", "claim_date"),
    )
