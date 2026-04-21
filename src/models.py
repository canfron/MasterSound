from pydantic import BaseModel, Field
from typing import Optional


class Customer(BaseModel):
    """Modelo de cliente"""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[str] = None


class Invoice(BaseModel):
    """Modelo de factura"""
    id: Optional[int] = None
    customer_id: int
    invoice_number: str
    date: str
    total: float
    status: str = "pending"
    items: list[dict] = []
    created_at: Optional[str] = None
