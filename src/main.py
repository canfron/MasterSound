from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import json

from src.database import (
    Base, Category, Supplier, Product, Customer, Invoice,
    Order, OrderItem, StockMove, get_db,
)
from src.models import (
    Category as CatPydantic, CategoryCreate, CategoryUpdate,
    Supplier as SupPydantic, SupplierCreate, SupplierUpdate,
    Product as ProdPydantic, ProductCreate, ProductUpdate,
    Customer as CustPydantic, CustomerCreate, CustomerUpdate,
    Invoice as InvPydantic, InvoiceCreate, InvoiceUpdate, InvoiceItem,
    Order as OrdPydantic, OrderCreate,
    StockMove as SMPydantic, StockMoveCreate,
    DashboardStats,
)

app = FastAPI(title="MasterSound - Gestión de Tienda", version="2.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── utilidades ──────────────────────────────────────────────

def _obj2dict(obj):
    """SQLAlchemy object → plain dict, JSON-safe."""
    cols = obj.__table__.columns.keys()
    d = {c: getattr(obj, c) for c in cols}
    if "items" in d and isinstance(d["items"], str):
        try:
            d["items"] = json.loads(d["items"])
        except Exception:
            d["items"] = []
    return d


def _gen_id(prefix: str = "ID") -> str:
    import random
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{random.randint(1000,9999)}"


# ── dashboard ──────────────────────────────────────────────

@app.get("/dashboard/stats")
async def dashboard_stats():
    db = next(get_db())
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    first_of_month = today.replace(day=1, hour=0, minute=0, second=0)
    # last day of month
    if now.month == 12:
        last_day = now.replace(month=1, year=now.year+1, day=1) - timedelta(days=1)
    else:
        last_day = now.replace(month=now.month+1, day=1) - timedelta(days=1)
    
    # Revenue del mes actual
    monthly_rev = db.query().with_entities(
        db.func.sum(Invoice.total)
    ).filter(
        Invoice.date >= first_of_month,
        Invoice.date <= last_day,
        Invoice.status == "paid",
    ).scalar() or 0
    
    total_rev = db.query(Invoice).with_entities(
        db.func.sum(Invoice.total)
    ).scalar() or 0
    
    pending_inv = db.query(Invoice).filter(Invoice.status == "pending").count()
    
    # Recent invoices (last 10)
    recent = db.query(Invoice).order_by(Invoice.date.desc()).limit(10).all()
    recent_list = []
    for inv in recent:
        d = _obj2dict(inv)
        d["customer_name"] = inv.customer.name if inv.customer else "N/A"
        d["category_name"] = None
        d["supplier_name"] = None
        recent_list.append(d)
    
    # Low stock
    low_stock = db.query(Product).filter(
        Product.stock < Product.min_stock
    ).all()
    
    # Stock by category
    categories = db.query(Category).all()
    cat_stock = []
    for cat in categories:
        total = db.query(Product).filter(
            Product.category_id == cat.id
        ).with_entities(db.func.sum(Product.stock)).scalar() or 0
        cat_stock.append({"category": cat.name, "total_stock": total})
    
    return DashboardStats(
        total_customers=db.query(Customer).count(),
        total_invoices=db.query(Invoice).count(),
        pending_invoices=pending_inv,
        total_products=db.query(Product).count(),
        low_stock_products=len(low_stock),
        monthly_revenue=float(monthly_rev),
        total_stock=db.query(Product).with_entities(db.func.sum(Product.stock)).scalar() or 0,
        total_revenue=float(total_rev),
        recent_invoices=recent_list,
        low_stock_list=[_obj2dict(p) for p in low_stock],
        stock_by_category=cat_stock,
    )


# ── CATEGORÍAS ─────────────────────────────────────────────

@app.get("/categories")
async def list_categories(skip: int = 0, limit: int = 100):
    db = next(get_db())
    cats = db.query(Category).offset(skip).limit(limit).all()
    return [_obj2dict(c) for c in cats]


@app.get("/categories/{cid}")
async def get_category(cid: int):
    db = next(get_db())
    c = db.query(Category).filter(Category.id == cid).first()
    if not c:
        raise HTTPException(404, "Categoría no encontrada")
    return _obj2dict(c)


@app.post("/categories")
async def create_category(cat: CategoryCreate):
    db = next(get_db())
    db_obj = Category(name=cat.name, description=cat.description)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return _obj2dict(db_obj)


@app.put("/categories/{cid}")
async def update_category(cid: int, cat: CategoryUpdate):
    db = next(get_db())
    c = db.query(Category).filter(Category.id == cid).first()
    if not c:
        raise HTTPException(404, "Categoría no encontrada")
    for k, v in cat.dict().items():
        if v is not None:
            setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return _obj2dict(c)


@app.delete("/categories/{cid}")
async def delete_category(cid: int):
    db = next(get_db())
    c = db.query(Category).filter(Category.id == cid).first()
    if not c:
        raise HTTPException(404, "Categoría no encontrada")
    db.delete(c)
    db.commit()
    return {"ok": True}


# ── PROVEEDORES ────────────────────────────────────────────

@app.get("/suppliers")
async def list_suppliers(skip: int = 0, limit: int = 100):
    db = next(get_db())
    s = db.query(Supplier).offset(skip).limit(limit).all()
    return [_obj2dict(x) for x in s]


@app.get("/suppliers/{sid}")
async def get_supplier(sid: int):
    db = next(get_db())
    s = db.query(Supplier).filter(Supplier.id == sid).first()
    if not s:
        raise HTTPException(404, "Proveedor no encontrado")
    return _obj2dict(s)


@app.post("/suppliers")
async def create_supplier(sup: SupplierCreate):
    db = next(get_db())
    db_obj = Supplier(
        name=sup.name, contact_name=sup.contact_name,
        email=sup.email, phone=sup.phone, address=sup.address,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return _obj2dict(db_obj)


@app.put("/suppliers/{sid}")
async def update_supplier(sid: int, sup: SupplierUpdate):
    db = next(get_db())
    s = db.query(Supplier).filter(Supplier.id == sid).first()
    if not s:
        raise HTTPException(404, "Proveedor no encontrado")
    for k, v in sup.dict().items():
        if v is not None:
            setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return _obj2dict(s)


@app.delete("/suppliers/{sid}")
async def delete_supplier(sid: int):
    db = next(get_db())
    s = db.query(Supplier).filter(Supplier.id == sid).first()
    if not s:
        raise HTTPException(404, "Proveedor no encontrado")
    db.delete(s)
    db.commit()
    return {"ok": True}


# ── PRODUCTOS ──────────────────────────────────────────────

@app.get("/products")
async def list_products(
    skip: int = 0, limit: int = 100,
    category: Optional[int] = None,
    supplier: Optional[int] = None,
    search: Optional[str] = None,
    low_stock: bool = False,
):
    db = next(get_db())
    q = db.query(Product)
    if category:
        q = q.filter(Product.category_id == category)
    if supplier:
        q = q.filter(Product.supplier_id == supplier)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    if low_stock:
        q = q.filter(Product.stock < Product.min_stock)
    products = q.offset(skip).limit(limit).all()
    out = []
    for p in products:
        d = _obj2dict(p)
        if p.category:
            d["category_name"] = p.category.name
        if p.supplier:
            d["supplier_name"] = p.supplier.name
        d["low_stock"] = p.stock < p.min_stock
        out.append(d)
    return out


@app.get("/products/{pid}")
async def get_product(pid: int):
    db = next(get_db())
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Producto no encontrado")
    d = _obj2dict(p)
    if p.category:
        d["category_name"] = p.category.name
    if p.supplier:
        d["supplier_name"] = p.supplier.name
    d["low_stock"] = p.stock < p.min_stock
    return d


@app.post("/products")
async def create_product(prod: ProductCreate):
    db = next(get_db())
    db_obj = Product(
        name=prod.name, description=prod.description,
        price=prod.price, category_id=prod.category_id,
        supplier_id=prod.supplier_id, stock=prod.stock,
        min_stock=prod.min_stock, code=prod.code,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    d = _obj2dict(db_obj)
    if db_obj.category:
        d["category_name"] = db_obj.category.name
    if db_obj.supplier:
        d["supplier_name"] = db_obj.supplier.name
    d["low_stock"] = db_obj.stock < db_obj.min_stock
    return d


@app.put("/products/{pid}")
async def update_product(pid: int, prod: ProductUpdate):
    db = next(get_db())
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Producto no encontrado")
    for k, v in prod.dict().items():
        if v is not None:
            setattr(p, k, v)
    db.commit()
    db.refresh(p)
    d = _obj2dict(p)
    if p.category:
        d["category_name"] = p.category.name
    if p.supplier:
        d["supplier_name"] = p.supplier.name
    d["low_stock"] = p.stock < p.min_stock
    return d


@app.delete("/products/{pid}")
async def delete_product(pid: int):
    db = next(get_db())
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Producto no encontrado")
    db.delete(p)
    db.commit()
    return {"ok": True}


# ── CLIENTES ───────────────────────────────────────────────

@app.get("/customers")
async def list_customers(skip: int = 0, limit: int = 100):
    db = next(get_db())
    cs = db.query(Customer).offset(skip).limit(limit).all()
    return [_obj2dict(c) for c in cs]


@app.get("/customers/search")
async def search_customers(q: str):
    db = next(get_db())
    cs = db.query(Customer).filter(
        Customer.name.ilike(f"%{q}%") |
        Customer.email.ilike(f"%{q}%")
    ).all()
    return [_obj2dict(c) for c in cs]


@app.get("/customers/{cid}")
async def get_customer(cid: int):
    db = next(get_db())
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    return _obj2dict(c)


@app.post("/customers")
async def create_customer(cust: CustomerCreate):
    db = next(get_db())
    db_obj = Customer(name=cust.name, email=cust.email,
                      phone=cust.phone, address=cust.address)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return _obj2dict(db_obj)


@app.put("/customers/{cid}")
async def update_customer(cid: int, cust: CustomerUpdate):
    db = next(get_db())
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    for k, v in cust.dict().items():
        if v is not None:
            setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return _obj2dict(c)


@app.delete("/customers/{cid}")
async def delete_customer(cid: int):
    db = next(get_db())
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    db.delete(c)
    db.commit()
    return {"ok": True}


# ── FACTURAS ───────────────────────────────────────────────

@app.get("/invoices")
async def list_invoices(
    skip: int = 0, limit: int = 100,
    status: Optional[str] = None,
):
    db = next(get_db())
    q = db.query(Invoice)
    if status:
        q = q.filter(Invoice.status == status)
    invs = q.offset(skip).limit(limit).all()
    out = []
    for inv in invs:
        d = _obj2dict(inv)
        d["customer_name"] = inv.customer.name if inv.customer else None
        d["quantity"] = len(d["items"])
        out.append(d)
    return out


@app.get("/invoices/{iid}")
async def get_invoice(iid: int):
    db = next(get_db())
    inv = db.query(Invoice).filter(Invoice.id == iid).first()
    if not inv:
        raise HTTPException(404, "Factura no encontrada")
    d = _obj2dict(inv)
    d["customer_name"] = inv.customer.name if inv.customer else None
    d["quantity"] = len(d["items"])
    return d


@app.post("/invoices")
async def create_invoice(inv: InvoiceCreate):
    db = next(get_db())
    c = db.query(Customer).filter(Customer.id == inv.customer_id).first()
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    
    if not inv.invoice_number:
        inv.invoice_number = _gen_id("INV")
    
    db_inv = Invoice(
        customer_id=inv.customer_id,
        invoice_number=inv.invoice_number,
        date=datetime.fromisoformat(inv.date.replace("Z", "+00:00")),
        total=inv.total,
        status=inv.status,
        items=json.dumps(inv.items or []),
    )
    db.add(db_inv)
    db.commit()
    db.refresh(db_inv)
    d = _obj2dict(db_inv)
    d["customer_name"] = c.name
    d["quantity"] = len(inv.items or [])
    return d


@app.put("/invoices/{iid}")
async def update_invoice(iid: int, inv: InvoiceUpdate):
    db = next(get_db())
    db_inv = db.query(Invoice).filter(Invoice.id == iid).first()
    if not db_inv:
        raise HTTPException(404, "Factura no encontrada")
    for k, v in inv.dict().items():
        if v is not None:
            setattr(db_inv, k, v)
    db.commit()
    db.refresh(db_inv)
    return _obj2dict(db_inv)


@app.put("/invoices/{iid}/status")
async def update_invoice_status(iid: int, status: str):
    db = next(get_db())
    db_inv = db.query(Invoice).filter(Invoice.id == iid).first()
    if not db_inv:
        raise HTTPException(404, "Factura no encontrada")
    db_inv.status = status
    db.commit()
    db.refresh(db_inv)
    return _obj2dict(db_inv)


@app.delete("/invoices/{iid}")
async def delete_invoice(iid: int):
    db = next(get_db())
    db_inv = db.query(Invoice).filter(Invoice.id == iid).first()
    if not db_inv:
        raise HTTPException(404, "Factura no encontrada")
    db.delete(db_inv)
    db.commit()
    return {"ok": True}


@app.get("/customers/{cid}/invoices")
async def get_customer_invoices(cid: int):
    db = next(get_db())
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    invs = db.query(Invoice).filter(Invoice.customer_id == cid).all()
    out = []
    for inv in invs:
        d = _obj2dict(inv)
        d["customer_name"] = c.name
        d["quantity"] = len(d["items"])
        out.append(d)
    return out


# ── PEDIDOS ─────────────────────────────────────────────────

@app.get("/orders")
async def list_orders(
    skip: int = 0, limit: int = 100,
    status: Optional[str] = None,
):
    db = next(get_db())
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    orders = q.offset(skip).limit(limit).all()
    out = []
    for o in orders:
        d = _obj2dict(o)
        d["customer_name"] = o.customer.name if o.customer else None
        d["supplier_name"] = o.supplier.name if o.supplier else None
        d["quantity"] = len(d["items"])
        out.append(d)
    return out


@app.get("/orders/{oid}")
async def get_order(oid: int):
    db = next(get_db())
    o = db.query(Order).filter(Order.id == oid).first()
    if not o:
        raise HTTPException(404, "Pedido no encontrado")
    d = _obj2dict(o)
    d["customer_name"] = o.customer.name if o.customer else None
    d["supplier_name"] = o.supplier.name if o.supplier else None
    d["quantity"] = len(d["items"])
    return d


@app.post("/orders")
async def create_order(order: OrderCreate):
    db = next(get_db())
    c = db.query(Customer).filter(Customer.id == order.customer_id).first()
    s = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    if not s:
        raise HTTPException(404, "Proveedor no encontrado")
    
    if not order.order_number:
        order.order_number = _gen_id("ORD")
    
    total = 0
    products_to_update = []
    for item in order.items:
        pid = item["product_id"]
        qty = item["quantity"]
        unit_price = item["unit_price"]
        db_prod = db.query(Product).get(pid)
        if not db_prod or db_prod.stock < qty:
            raise HTTPException(400, f"Stock insuficiente para producto {pid}")
        products_to_update.append((db_prod, qty))
        total += qty * unit_price
    
    db_order = Order(
        customer_id=order.customer_id,
        supplier_id=order.supplier_id,
        order_number=order.order_number,
        date=datetime.fromisoformat(order.date.replace("Z", "+00:00")),
        total=total,
        status="pending",
        items=json.dumps(order.items),
        notes=order.notes,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    d = _obj2dict(db_order)
    d["customer_name"] = c.name
    d["supplier_name"] = s.name
    d["quantity"] = len(order.items)
    return d


@app.put("/orders/{oid}/status")
async def update_order_status(oid: int, status: str):
    db = next(get_db())
    o = db.query(Order).filter(Order.id == oid).first()
    if not o:
        raise HTTPException(404, "Pedido no encontrado")
    
    if status == "received":
        try:
            items = json.loads(o.items) if o.items else []
        except Exception:
            items = []
        for item in items:
            pid = item["product_id"]
            qty = item["quantity"]
            db_prod = db.query(Product).get(pid)
            if db_prod:
                db_prod.stock += qty
                db.add(StockMove(
                    product_id=pid, quantity=qty, type="in",
                    reference=o.order_number, notes="Recibido de pedido",
                ))
    
    o.status = status
    db.commit()
    db.refresh(o)
    d = _obj2dict(o)
    d["customer_name"] = o.customer.name if o.customer else None
    d["supplier_name"] = o.supplier.name if o.supplier else None
    d["quantity"] = len(d["items"])
    return d


@app.delete("/orders/{oid}")
async def delete_order(oid: int):
    db = next(get_db())
    o = db.query(Order).filter(Order.id == oid).first()
    if not o:
        raise HTTPException(404, "Pedido no encontrado")
    db.delete(o)
    db.commit()
    return {"ok": True}


# ── MOVIMIENTOS DE STOCK ───────────────────────────────────

@app.get("/stock-moves")
async def list_stock_moves(skip: int = 0, limit: int = 100):
    db = next(get_db())
    moves = db.query(StockMove).order_by(StockMove.date.desc()).offset(skip).limit(limit).all()
    out = []
    for m in moves:
        d = _obj2dict(m)
        d["product_name"] = m.product.name if m.product else None
        out.append(d)
    return out


@app.post("/stock-moves")
async def create_stock_move(move: StockMoveCreate):
    db = next(get_db())
    prod = db.query(Product).get(move.product_id)
    if not prod:
        raise HTTPException(404, "Producto no encontrado")
    if prod.stock + move.quantity < 0:
        raise HTTPException(400, "Stock insuficiente")
    
    prod.stock += move.quantity
    db_move = StockMove(
        product_id=move.product_id, quantity=move.quantity,
        type=move.type, reference=move.reference, notes=move.notes,
    )
    db.add(db_move)
    db.commit()
    db.refresh(db_move)
    d = _obj2dict(db_move)
    d["product_name"] = prod.name
    return d


# ── ROOT ───────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "message": "MasterSound API - Gestión Completa de Tienda",
        "version": "2.0.0",
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)