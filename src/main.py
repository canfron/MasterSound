from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional

from src.database import Base, Customer, Invoice, get_db
from src.models import Customer as CustomerPydantic, Invoice as InvoicePydantic

app = FastAPI(title="MasterSound API")

# Pydantic schemas for request bodies
class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class InvoiceCreate(BaseModel):
    customer_id: int
    invoice_number: str
    date: str
    total: float
    items: Optional[List[dict]] = []


@app.get("/")
async def root():
    return {"message": "MasterSound API - Clientes y Facturación con SQLite"}


# === CLIENTES ===

@app.get("/customers", response_model=List[CustomerPydantic])
async def list_customers(skip: int = 0, limit: int = 100):
    db = next(get_db())
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return [CustomerPydantic(**c.__dict__) for c in customers]


@app.get("/customers/{customer_id}", response_model=CustomerPydantic)
async def get_customer(customer_id: int):
    db = next(get_db())
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return CustomerPydantic(**customer.__dict__)


@app.post("/customers", response_model=CustomerPydantic)
async def create_customer(customer: CustomerCreate):
    db = next(get_db())
    db_customer = Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        address=customer.address
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return CustomerPydantic(**db_customer.__dict__)


@app.put("/customers/{customer_id}", response_model=CustomerPydantic)
async def update_customer(customer_id: int, customer: CustomerUpdate):
    db = next(get_db())
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    for field, value in customer.dict().items():
        if value is not None:
            setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return CustomerPydantic(**db_customer.__dict__)


@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int):
    db = next(get_db())
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(db_customer)
    db.commit()
    return {"message": "Cliente eliminado"}


# === FACTURACIÓN ===

@app.get("/invoices", response_model=List[InvoicePydantic])
async def list_invoices(skip: int = 0, limit: int = 100):
    db = next(get_db())
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return [InvoicePydantic(**inv.__dict__) for inv in invoices]


@app.get("/invoices/{invoice_id}", response_model=InvoicePydantic)
async def get_invoice(invoice_id: int):
    db = next(get_db())
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return InvoicePydantic(**invoice.__dict__)


@app.post("/invoices", response_model=InvoicePydantic)
async def create_invoice(invoice: InvoiceCreate):
    db = next(get_db())
    
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db_invoice = Invoice(
        customer_id=invoice.customer_id,
        invoice_number=invoice.invoice_number,
        date=datetime.fromisoformat(invoice.date.replace("Z", "+00:00")).astimezone(timezone.utc),
        total=invoice.total,
        items=str(invoice.items) if invoice.items else "[]",
        status="pending"
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return InvoicePydantic(**db_invoice.__dict__)


@app.put("/invoices/{invoice_id}", response_model=InvoicePydantic)
async def update_invoice(invoice_id: int, invoice: InvoiceCreate):
    db = next(get_db())
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Validate customer still exists
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    for field, value in invoice.dict().items():
        if field == "items":
            setattr(db_invoice, field, str(value) if value else "[]")
        else:
            setattr(db_invoice, field, value)
    
    db.commit()
    db.refresh(db_invoice)
    return InvoicePydantic(**db_invoice.__dict__)


@app.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: int):
    db = next(get_db())
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    db.delete(db_invoice)
    db.commit()
    return {"message": "Factura eliminada"}


@app.get("/customers/{customer_id}/invoices", response_model=List[InvoicePydantic])
async def get_customer_invoices(customer_id: int):
    db = next(get_db())
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    invoices = db.query(Invoice).filter(Invoice.customer_id == customer_id).all()
    return [InvoicePydantic(**inv.__dict__) for inv in invoices]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
