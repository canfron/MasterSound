from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    price: float
    stock: Optional[int] = 0
    is_active: Optional[bool] = True

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SaleBase(BaseModel):
    product_id: int
    quantity: int
    payment_method: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    total_amount: float
    sale_date: datetime

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    customer_name: str
    customer_email: str
    status: Optional[str] = "pending"
    total_amount: float
    address: Optional[str] = None
    delivery_date: Optional[datetime] = None

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    order_date: datetime

    class Config:
        orm_mode = True

class StockMovementBase(BaseModel):
    product_id: int
    quantity: int
    movement_type: str  # "in" or "out"
    reference: Optional[str] = None

class StockMovementCreate(StockMovementBase):
    pass

class StockMovement(StockMovementBase):
    id: int
    movement_date: datetime

    class Config:
        orm_mode = True
