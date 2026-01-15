from pydantic import BaseModel, Field

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)

class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        from_attributes = True

class RecordCreate(BaseModel):
    year: int = Field(ge=1900, le=2100)
    value_kwh: float = Field(gt=0)
    category_id: int

class RecordOut(BaseModel):
    id: int
    year: int
    value_kwh: float
    category_id: int

    class Config:
        from_attributes = True
