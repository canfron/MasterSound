from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone

Base = declarative_base()


class Category(Base):
    """Modelo de categoría"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    products = relationship("Product", back_populates="category")


class Supplier(Base):
    """Modelo de proveedor"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    products = relationship("Product", back_populates="supplier")


class Product(Base):
    """Modelo de producto"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=10)
    code = Column(String(50), unique=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    
    # Relación con pedidos
    order_items = relationship("OrderItem", back_populates="product")
    stock_moves = relationship("StockMove", back_populates="product")


class Customer(Base):
    """Modelo de cliente"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    invoices = relationship("Invoice", back_populates="customer")
    orders = relationship("Order", back_populates="customer")


class Invoice(Base):
    """Modelo de factura"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False)
    date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    total = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    items = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    customer = relationship("Customer", back_populates="invoices")


class Order(Base):
    """Modelo de pedido (a proveedor)"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    total = Column(Float, nullable=False, default=0)
    status = Column(String(20), default="pending")
    items = Column(Text, nullable=True)  # JSON string
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    customer = relationship("Customer", back_populates="orders")
    supplier = relationship("Supplier")


class OrderItem(Base):
    """Item de pedido"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    
    product = relationship("Product", back_populates="order_items")


class StockMove(Base):
    """Movimiento de stock"""
    __tablename__ = "stock_moves"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    type = Column(String(20), nullable=False)  # in, out, adjustment
    reference = Column(String(100), nullable=True)
    notes = Column(String(500), nullable=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    product = relationship("Product", back_populates="stock_moves")


# ─── Configuración DB ───
SQLALCHEMY_DATABASE_URL = "sqlite:///./mastersound.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    """Generador de sesiones para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
