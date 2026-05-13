from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Categorías ───

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Category(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None


# ─── Proveedores ───

class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class Supplier(BaseModel):
    id: Optional[int] = None
    name: str
    contact_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[str] = None


# ─── Productos ───

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    stock: int = Field(default=0, ge=0)
    min_stock: int = Field(default=10, ge=0)
    code: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    code: Optional[str] = None


class Product(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    stock: int
    min_stock: int
    code: Optional[str] = None
    created_at: Optional[str] = None


# ─── Clientes (existente, mantenido) ───

class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class Customer(BaseModel):
    id: Optional[int] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[str] = None


# ─── Facturas (existente, mantenido) ───

class InvoiceCreate(BaseModel):
    customer_id: int
    invoice_number: str
    date: str
    total: float
    items: Optional[List[dict]] = []
    status: str = "pending"


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None


class InvoiceItem(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    total: float


class Invoice(BaseModel):
    id: Optional[int] = None
    customer_id: int
    invoice_number: str
    date: str
    total: float
    status: str
    items: Optional[List[InvoiceItem]] = []
    created_at: Optional[str] = None
    customer_name: Optional[str] = None


# ─── Pedidos ───

class OrderCreate(BaseModel):
    customer_id: int
    supplier_id: int
    order_number: str
    date: str
    items: List[dict]  # [{"product_id": int, "quantity": int, "unit_price": float}]
    notes: Optional[str] = None


class Order(BaseModel):
    id: Optional[int] = None
    customer_id: int
    supplier_id: int
    order_number: str
    date: str
    total: float
    status: str  # pending, received, cancelled
    items: Optional[List[dict]] = []
    notes: Optional[str] = None
    created_at: Optional[str] = None
    customer_name: Optional[str] = None
    supplier_name: Optional[str] = None


# ─── Movimientos de Stock ───

class StockMoveCreate(BaseModel):
    product_id: int
    quantity: int  # positivo=entrada, negativo=salida
    type: str  # in, out, adjustment
    reference: Optional[str] = None
    notes: Optional[str] = None


class StockMove(BaseModel):
    id: Optional[int] = None
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    type: str
    reference: Optional[str] = None
    notes: Optional[str] = None
    date: str
    created_at: Optional[str] = None


# ─── Dashboard ───

class DashboardStats(BaseModel):
    total_customers: int = 0
    total_invoices: int = 0
    pending_invoices: int = 0
    total_products: int = 0
    low_stock_products: int = 0
    total_orders: int = 0
    monthly_revenue: float = 0
    total_stock: int = 0
    total_revenue: float = 0
    recent_invoices: List[dict] = []
    low_stock_list: List[dict] = []
    stock_by_category: List[dict] = []
