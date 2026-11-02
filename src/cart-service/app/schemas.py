
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# Request schema for adding a product to cart
class CartItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0)


# Request schema for updating product quantity
class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


# Response schema for individual cart items
class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Response schema for complete cart
class CartResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    items: list[CartItemResponse]

    model_config = ConfigDict(from_attributes=True)
