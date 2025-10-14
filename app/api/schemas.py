from pydantic import BaseModel, Field, ConfigDict

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