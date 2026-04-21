import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestCustomers:
    def test_list_customers_empty(self):
        response = client.get("/customers")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_customer(self):
        data = {"name": "Juan Pérez", "email": "juan@test.com"}
        response = client.post("/customers", json=data)
        assert response.status_code in (200, 201)
        json = response.json()
        assert json["name"] == "Juan Pérez"
        assert json["email"] == "juan@test.com"
        assert "id" in json

    def test_get_customer(self):
        # Create first
        data = {"name": "Ana López", "email": "ana@test.com"}
        response = client.post("/customers", json=data)
        json = response.json()
        customer_id = json["id"]
        
        # Get
        response = client.get(f"/customers/{customer_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Ana López"

    def test_update_customer(self):
        # Create first
        data = {"name": "Carlos Ruiz", "email": "carlos@test.com"}
        response = client.post("/customers", json=data)
        json = response.json()
        customer_id = json["id"]
        
        # Update
        update_data = {"name": "Carlos Actualizado", "email": "carlos2@test.com"}
        response = client.put(f"/customers/{customer_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Carlos Actualizado"

    def test_delete_customer(self):
        # Create first
        data = {"name": "Test Delete", "email": "delete@test.com"}
        response = client.post("/customers", json=data)
        json = response.json()
        customer_id = json["id"]
        
        # Delete
        response = client.delete(f"/customers/{customer_id}")
        assert response.status_code == 200
        
        # Verify deleted
        response = client.get(f"/customers/{customer_id}")
        assert response.status_code == 404


class TestInvoices:
    def test_list_invoices_empty(self):
        response = client.get("/invoices")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_invoice(self):
        # Create customer first
        customer_data = {"name": "Cliente Test", "email": "cliente@test.com"}
        response = client.post("/customers", json=customer_data)
        customer_json = response.json()
        customer_id = customer_json["id"]
        
        # Create invoice
        invoice_data = {
            "customer_id": customer_id,
            "invoice_number": "INV-001",
            "date": "2026-04-21",
            "total": 150.00,
            "items": [{"product": "Producto A", "qty": 2, "price": 75.00}]
        }
        response = client.post("/invoices", json=invoice_data)
        assert response.status_code in (200, 201)
        json = response.json()
        assert json["invoice_number"] == "INV-001"
        assert json["total"] == 150.00

    def test_get_invoice(self):
        # Create customer first
        customer_data = {"name": "Cliente Test", "email": "cliente@test.com"}
        response = client.post("/customers", json=customer_data)
        customer_json = response.json()
        customer_id = customer_json["id"]
        
        # Create invoice
        invoice_data = {
            "customer_id": customer_id,
            "invoice_number": "INV-002",
            "date": "2026-04-21",
            "total": 200.00
        }
        response = client.post("/invoices", json=invoice_data)
        json = response.json()
        invoice_id = json["id"]
        
        # Get
        response = client.get(f"/invoices/{invoice_id}")
        assert response.status_code == 200
        assert response.json()["invoice_number"] == "INV-002"

    def test_get_customer_invoices(self):
        # Create customer
        customer_data = {"name": "Cliente Facturas", "email": "facturas@test.com"}
        response = client.post("/customers", json=customer_data)
        customer_json = response.json()
        customer_id = customer_json["id"]
        
        # Create invoices
        for i in range(3):
            invoice_data = {
                "customer_id": customer_id,
                "invoice_number": f"INV-{i}",
                "date": "2026-04-21",
                "total": 100.00
            }
            client.post("/invoices", json=invoice_data)
        
        # Get customer invoices
        response = client.get(f"/customers/{customer_id}/invoices")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_create_invoice_invalid_customer(self):
        invoice_data = {
            "customer_id": 9999,
            "invoice_number": "INV-INVALID",
            "date": "2026-04-21",
            "total": 100.00
        }
        response = client.post("/invoices", json=invoice_data)
        assert response.status_code == 404
