
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime


# Schema for creating a product
class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str = Field(min_length=1, max_length=100)
    stock_quantity: int = Field(default=0, ge=0)


# Schema for updating a product
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    category: str | None = Field(default=None, min_length=1, max_length=100)
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


# Schema for returning product details
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    category: str
    stock_quantity: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
