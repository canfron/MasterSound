"""
MasterSound API - Tests completos
Cubre: Categories, Suppliers, Products, Customers, Invoices, Orders, Stock Moves, Dashboard
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


def _get_list(url, **params):
    r = client.get(url, params=params)
    assert r.status_code == 200
    return r.json()


# Constants
URLS = {
    "category": "/categories",
    "supplier": "/suppliers",
    "product": "/products",
    "customer": "/customers",
    "invoice": "/invoices",
    "order": "/orders",
    "stock-move": "/stock-moves",
}

client = TestClient(app)



# ---------------------------------------------------------------------------
# ── CATEGORIES ─────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestCategories:
    def test_list_empty(self):
        resp = _get_list(URLS["category"])
        assert resp == []

    def test_crud(self):
        # Create
        r = client.post(URLS["category"], json={"name": "Guitarras", "description": "Cuerdas"})
        assert r.status_code in (200, 201)
        cat = r.json()
        assert cat["name"] == "Guitarras"
        assert "id" in cat

        # Read
        r = client.get(f"{URLS['category']}/{cat['id']}")
        assert r.status_code == 200
        assert r.json()["name"] == "Guitarras"

        # Update
        r = client.put(f"{URLS['category']}/{cat['id']}", json={"name": "Guitarras Pro"})
        assert r.status_code == 200
        assert r.json()["name"] == "Guitarras Pro"

        # Delete
        r = client.delete(f"{URLS['category']}/{cat['id']}")
        assert r.json()["ok"] is True
        assert client.get(f"{URLS['category']}/{cat['id']}").status_code == 404


# ---------------------------------------------------------------------------
# ── SUPPLIERS ──────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestSuppliers:
    def test_crud(self):
        r = client.post(URLS["supplier"], json={
            "name": "Distribuidora Sur",
            "contact_name": "Marta",
            "email": "marta@sur.com",
            "phone": "600123456",
            "address": "Madrid",
        })
        assert r.status_code in (200, 201)
        sup = r.json()
        assert sup["name"] == "Distribuidora Sur"
        assert "id" in sup

        r = client.get(f"{URLS['supplier']}/{sup['id']}")
        assert r.status_code == 200 and r.json()["email"] == "marta@sur.com"

        r = client.put(f"{URLS['supplier']}/{sup['id']}", json={"phone": "600999999"})
        assert r.status_code == 200 and r.json()["phone"] == "600999999"

        r = client.delete(f"{URLS['supplier']}/{sup['id']}")
        assert r.json()["ok"] is True

    def test_list_with_pagination(self):
        for i in range(3):
            client.post(URLS["supplier"], json={
                "name": f"Supplier {i}", "contact_name": f"Contact {i}",
            })
        result = _get_list(URLS["supplier"], limit=2, skip=0)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# ── PRODUCTS ────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestProducts:
    def _setup(self):
        """Crea category, supplier, devuelve ids."""
        rc = client.post(URLS["category"], json={"name": "Drums"})
        cat_id = rc.json()["id"]
        rs = client.post(URLS["supplier"], json={"name": "Drum Co", "contact_name": "Dan"})
        sup_id = rs.json()["id"]
        return cat_id, sup_id

    def test_crud(self):
        cat_id, sup_id = self._setup()
        r = client.post(URLS["product"], json={
            "name": "Batería Acústica",
            "description": "5 piezas",
            "price": 899.99,
            "category_id": cat_id,
            "supplier_id": sup_id,
            "stock": 5,
            "min_stock": 2,
            "code": "DRM-001",
        })
        assert r.status_code in (200, 201)
        prod = r.json()
        assert prod["name"] == "Batería Acústica"
        assert prod["price"] == 899.99
        assert prod["category_name"] == "Drums"
        assert prod["supplier_name"] == "Drum Co"
        assert "id" in prod

        # Get
        r = client.get(f"{URLS['product']}/{prod['id']}")
        assert r.status_code == 200

        # Update
        r = client.put(f"{URLS['product']}/{prod['id']}", json={"price": 799.99})
        assert r.status_code == 200 and r.json()["price"] == 799.99

        # Delete
        r = client.delete(f"{URLS['product']}/{prod['id']}")
        assert r.json()["ok"] is True

    def test_search(self):
        cat_id, sup_id = self._setup()
        client.post(URLS["product"], json={"name": "Guitarra Eléctrica", "price": 500, "category_id": cat_id, "supplier_id": sup_id})
        client.post(URLS["product"], json={"name": "Guitarra Clásica", "price": 300, "category_id": cat_id, "supplier_id": sup_id})
        result = _get_list(URLS["product"], search="Guitarra")
        assert len(result) == 2

    def test_low_stock_filter(self):
        cat_id, sup_id = self._setup()
        client.post(URLS["product"], json={"name": "Bajo", "price": 200, "stock": 1, "min_stock": 5, "category_id": cat_id, "supplier_id": sup_id})
        client.post(URLS["product"], json={"name": "Pedal", "price": 50, "stock": 50, "min_stock": 10, "category_id": cat_id, "supplier_id": sup_id})
        low = _get_list(URLS["product"], low_stock=True)
        assert len(low) == 1 and low[0]["name"] == "Bajo"
        assert low[0]["low_stock"] is True

    def test_filters_combined(self):
        cat_id, sup_id = self._setup()
        client.post(URLS["product"], json={"name": "Amp", "price": 150, "stock": 10, "category_id": cat_id, "supplier_id": sup_id})
        result = _get_list(URLS["product"], category=cat_id, limit=1, skip=0)
        assert len(result) == 1

    def test_create_validation(self):
        with pytest.raises(Exception):
            client.post(URLS["product"], json={"name": "", "price": -1, "stock": -5})


# ---------------------------------------------------------------------------
# ── CUSTOMERS ───────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestCustomers:
    def test_crud(self):
        r = client.post(URLS["customer"], json={"name": "Juan", "email": "juan@test.com"})
        assert r.status_code in (200, 201)
        c = r.json()
        assert "id" in c

        r = client.get(f"{URLS['customer']}/{c['id']}")
        assert r.status_code == 200 and r.json()["name"] == "Juan"

        r = client.put(f"{URLS['customer']}/{c['id']}", json={"email": "juan2@test.com"})
        assert r.status_code == 200 and r.json()["email"] == "juan2@test.com"

        r = client.delete(f"{URLS['customer']}/{c['id']}")
        assert r.status_code == 200
        assert client.get(f"{URLS['customer']}/{c['id']}").status_code == 404

    def test_search(self):
        client.post(URLS["customer"], json={"name": "Ana López", "email": "ana@test.com"})
        client.post(URLS["customer"], json={"name": "Ana García", "email": "ana2@test.com"})
        r = client.get(f"{URLS['customer']}/search", params={"q": "Ana"})
        assert r.status_code == 200 and len(r.json()) == 2

    def test_list_pagination(self):
        for i in range(4):
            client.post(URLS["customer"], json={"name": f"C{i}", "email": f"c{i}@test.com"})
        r = _get_list(URLS["customer"], limit=2, skip=0)
        assert len(r) == 2


# ---------------------------------------------------------------------------
# ── INVOICES ────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestInvoices:
    def _setup_customer(self):
        r = client.post(URLS["customer"], json={"name": "Cliente Inv", "email": "inv@test.com"})
        return r.json()["id"]

    def test_create(self, test_customer_id):
        cid = test_customer_id
        r = client.post(URLS["invoice"], json={
            "customer_id": cid,
            "invoice_number": "INV-100",
            "date": "2026-06-01",
            "total": 500.0,
            "items": [{"product_id": 1, "quantity": 2, "unit_price": 250.0}],
        })
        assert r.status_code in (200, 201)
        inv = r.json()
        assert inv["invoice_number"] == "INV-100"
        assert inv["customer_name"] == "Cliente Inv"

    def test_get(self, test_customer_id):
        cid = test_customer_id
        r = client.post(URLS["invoice"], json={
            "customer_id": cid, "invoice_number": "INV-101",
            "date": "2026-06-01", "total": 300.0,
        })
        iid = r.json()["id"]
        r = client.get(f"{URLS['invoice']}/{iid}")
        assert r.status_code == 200 and r.json()["total"] == 300.0

    def test_update_status(self, test_customer_id):
        cid = test_customer_id
        r = client.post(URLS["invoice"], json={
            "customer_id": cid, "invoice_number": "INV-102",
            "date": "2026-06-01", "total": 100.0,
        })
        iid = r.json()["id"]
        r = client.put(f"{URLS['invoice']}/{iid}/status", params={"status": "paid"})
        assert r.status_code == 200 and r.json()["status"] == "paid"

    def test_invalid_customer(self):
        r = client.post(URLS["invoice"], json={
            "customer_id": 99999, "invoice_number": "INV-BAD",
            "date": "2026-06-01", "total": 10.0,
        })
        assert r.status_code == 404

    def test_list_filter_status(self, test_customer_id):
        cid = test_customer_id
        client.post(URLS["invoice"], json={"customer_id": cid, "invoice_number": "A", "date": "2026-06-01", "total": 10})
        r = _get_list(URLS["invoice"], status="pending")
        assert len(r) >= 1

    def test_customer_invoices(self, test_customer_id):
        cid = test_customer_id
        for i in range(3):
            client.post(URLS["invoice"], json={
                "customer_id": cid, "invoice_number": f"CI-{i}",
                "date": "2026-06-01", "total": 50.0,
            })
        r = client.get(f"{URLS['customer']}/{cid}/invoices")
        assert r.status_code == 200 and len(r.json()) == 3

    def test_get_nonexistent(self):
        r = client.get(f"{URLS['invoice']}/99999")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# ── ORDERS ──────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestOrders:
    def _setup_full(self):
        """Cliente + proveedor + producto con stock."""
        rc = client.post(URLS["customer"], json={"name": "Comprador"})
        cid = rc.json()["id"]
        rs = client.post(URLS["supplier"], json={"name": "Provee X", "contact_name": "Bob"})
        sid = rs.json()["id"]
        r = client.post(URLS["product"], json={
            "name": "Cuerda", "price": 10.0, "stock": 100, "min_stock": 5,
        })
        pid = r.json()["id"]
        return cid, sid, pid

    def test_create(self):
        cid, sid, pid = self._setup_full()
        r = client.post(URLS["order"], json={
            "customer_id": cid, "supplier_id": sid,
            "order_number": "ORD-001", "date": "2026-06-01",
            "items": [{"product_id": pid, "quantity": 3, "unit_price": 10.0}],
        })
        assert r.status_code in (200, 201)
        order = r.json()
        assert order["customer_name"] == "Comprador"
        assert order["supplier_name"] == "Provee X"
        assert order["total"] == 30.0

    def test_insufficient_stock(self):
        cid, sid, pid = self._setup_full()
        r = client.post(URLS["order"], json={
            "customer_id": cid, "supplier_id": sid,
            "order_number": "ORD-BAD", "date": "2026-06-01",
            "items": [{"product_id": pid, "quantity": 9999, "unit_price": 1.0}],
        })
        assert r.status_code == 400

    def test_update_status_received(self):
        cid, sid, pid = self._setup_full()
        r = client.post(URLS["order"], json={
            "customer_id": cid, "supplier_id": sid,
            "order_number": "ORD-REP", "date": "2026-06-01",
            "items": [{"product_id": pid, "quantity": 10, "unit_price": 1.0}],
        })
        oid = r.json()["id"]
        # Get stock before
        before = client.get(f"{URLS['product']}/{pid}").json()["stock"]
        # Receive
        r = client.put(f"{URLS['order']}/{oid}/status", params={"status": "received"})
        assert r.status_code == 200 and r.json()["status"] == "received"
        # Stock should be before + 10
        after = client.get(f"{URLS['product']}/{pid}").json()["stock"]
        assert after == before + 10

    def test_get_nonexistent(self):
        r = client.get(f"{URLS['order']}/99999")
        assert r.status_code == 404

    def test_delete(self):
        cid, sid, pid = self._setup_full()
        r = client.post(URLS["order"], json={
            "customer_id": cid, "supplier_id": sid,
            "order_number": "ORD-DEL", "date": "2026-06-01",
            "items": [{"product_id": pid, "quantity": 1, "unit_price": 1.0}],
        })
        oid = r.json()["id"]
        r = client.delete(f"{URLS['order']}/{oid}")
        assert r.status_code == 200 and r.json()["ok"] is True


# ---------------------------------------------------------------------------
# ── STOCK MOVES ─────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestStockMoves:
    def _setup(self):
        client.post(URLS["product"], json={"name": "Campana", "price": 20.0, "stock": 10})
        return client.get(URLS["product"]).json()[0]["id"]

    def test_create(self):
        pid = self._setup()
        r = client.post(URLS["stock-move"], json={
            "product_id": pid, "quantity": 5, "type": "in",
            "reference": "ADJ-001", "notes": "Ajuste inventario",
        })
        assert r.status_code in (200, 201)
        assert r.json()["product_name"] == "Campana"

    def test_list_desc(self):
        pid = self._setup()
        for i in range(3):
            client.post(URLS["stock-move"], json={
                "product_id": pid, "quantity": 1, "type": "in",
            })
        r = _get_list(URLS["stock-move"], limit=1, skip=0)
        assert len(r) == 1

    def test_insufficient_stock(self):
        pid = self._setup()
        r = client.post(URLS["stock-move"], json={
            "product_id": pid, "quantity": -999, "type": "out",
        })
        assert r.status_code == 400

    def test_invalid_product(self):
        r = client.post(URLS["stock-move"], json={
            "product_id": 99999, "quantity": 5, "type": "in",
        })
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# ── DASHBOARD ───────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestDashboard:
    def test_stats(self):
        r = client.get("/dashboard/stats")
        assert r.status_code == 200
        data = r.json()
        assert "total_customers" in data
        assert "total_invoices" in data
        assert "total_products" in data
        assert "monthly_revenue" in data
        assert "total_revenue" in data
        assert "low_stock_products" in data

    def test_stats_with_data(self):
        # Create some data
        rc = client.post(URLS["category"], json={"name": "TestCat"})
        rs = client.post(URLS["supplier"], json={"name": "TestSup", "contact_name": "X"})
        r = client.post(URLS["product"], json={"name": "Prod1", "price": 100, "stock": 5, "min_stock": 10, "category_id": rc.json()["id"], "supplier_id": rs.json()["id"]})
        rc2 = client.post(URLS["customer"], json={"name": "DashClient"})
        cid = rc2.json()["id"]
        client.post(URLS["invoice"], json={"customer_id": cid, "invoice_number": "D-001", "date": "2026-06-01", "total": 1000.0})
        client.post(URLS["invoice"], json={"customer_id": cid, "invoice_number": "D-002", "date": "2026-06-01", "total": 200.0, "status": "paid"})

        r = client.get("/dashboard/stats")
        data = r.json()
        assert data["total_products"] == 1
        assert data["low_stock_products"] >= 1
        assert data["total_customers"] == 1
        assert data["total_invoices"] >= 2
        assert data["recent_invoices"] != []


# ---------------------------------------------------------------------------
# ── UTILITY ─────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestRoot:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "MasterSound API" in r.json()["message"]


# ---------------------------------------------------------------------------
# ── FIXTURES AUXILIARES ─────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

@pytest.fixture
def test_customer_id():
    """Cliente de prueba compartido por tests de invoices."""
    r = client.post(URLS["customer"], json={"name": "TestInvoice", "email": "testinv@test.com"})
    return r.json()["id"]
