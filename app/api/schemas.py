from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from pydantic import field_validator, model_validator

class OwnerOut(BaseModel):
    id: int
    name: str
    email: str | None = None
    model_config = ConfigDict(from_attributes=True)

class CarOut(BaseModel):
    id: int
    vin: str
    make: str | None = None
    model: str | None = None
    # Expose camelCase in JSON while reading from the ORM's snake_case attribute
    year_of_manufacture: int | None = Field(
        default=None,
        serialization_alias="yearOfManufacture",
    )
    owner: OwnerOut

    model_config = ConfigDict(
        from_attributes=True,  # allow building from ORM objects
        populate_by_name=True  # enables alias-aware dumps when needed
    )

class PolicyCreate(BaseModel):
    provider: str | None = None
    start_date: date = Field(validation_alias="startDate")
    end_date: date = Field(validation_alias="endDate")

    @field_validator("start_date", "end_date")
    @classmethod
    def _in_range(cls, v: date):
        if v.year < 1900 or v.year > 2100:
            raise ValueError("Date must be between 1900 and 2100")
        return v

    @model_validator(mode="after")
    def _end_after_start(self):
        if self.end_date < self.start_date:
            raise ValueError("endDate must be on or after startDate")
        return self


class PolicyOut(BaseModel):
    id: int
    car_id: int = Field(serialization_alias="carId")
    provider: str | None = None
    start_date: date = Field(serialization_alias="startDate")
    end_date: date = Field(serialization_alias="endDate")
    model_config = ConfigDict(from_attributes=True)


class ValidityOut(BaseModel):
    car_id: int = Field(serialization_alias="carId")
    date: date
    valid: bool
    model_config = ConfigDict(populate_by_name=True)