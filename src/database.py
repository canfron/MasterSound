from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone

Base = declarative_base()


class Customer(Base):
    """Modelo de cliente"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relación con facturas
    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")


class Invoice(Base):
    """Modelo de factura"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    total = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    items = Column(Text, nullable=True)  # JSON string de items
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relación con cliente
    customer = relationship("Customer", back_populates="invoices")


# Configuración de base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./mastersound.db"

# Crear engine con check_same_thread=False para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Crear session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Helper para obtener session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
